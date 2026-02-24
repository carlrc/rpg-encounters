import { Construct } from "constructs";
import { S3Backend, TerraformOutput, TerraformStack } from "cdktf";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import { SecurityGroup } from "@cdktf/provider-aws/lib/security-group";
import { DbSubnetGroup } from "@cdktf/provider-aws/lib/db-subnet-group";
import { DbInstance } from "@cdktf/provider-aws/lib/db-instance";

type DbStackProps = {
  region: string;
  stateBucketName: string;
  resourcePrefix: string;
  vpcId: string;
  subnetIds: string[];
  ec2SecurityGroupId: string;
  dbUsername: string;
  dbPassword: string;
};

export class DbStack extends TerraformStack {
  private endpointHost: string;

  constructor(scope: Construct, id: string, props: DbStackProps) {
    super(scope, id);

    new AwsProvider(this, "aws-default", {
      alias: "default",
      region: props.region,
    });

    new S3Backend(this, {
      bucket: props.stateBucketName,
      key: "db/prd/terraform.tfstate",
      region: props.region,
    });

    const dbSg = new SecurityGroup(this, "rds-sg", {
      name: `${props.resourcePrefix}-rds`,
      vpcId: props.vpcId,
      ingress: [
        {
          // Postgres port expected by the backend DATABASE_URL.
          fromPort: 5432,
          toPort: 5432,
          protocol: "TCP",
          securityGroups: [props.ec2SecurityGroupId],
        },
      ],
      egress: [
        // Keep outbound traffic inside VPC only; inbound remains SG-restricted above.
        { fromPort: 0, toPort: 0, protocol: "-1", cidrBlocks: ["10.0.0.0/16"] },
      ],
    });

    const dbSubnetGroup = new DbSubnetGroup(this, "db-subnet-group", {
      name: `${props.resourcePrefix}-db-subnet-group`,
      subnetIds: props.subnetIds,
      tags: {
        service: "rpg-encounters",
        component: "database",
      },
    });

    const db = new DbInstance(this, "rds-postgres", {
      identifier: `${props.resourcePrefix}-postgres`,
      engine: "postgres",
      instanceClass: "db.t4g.micro",
      // RDS Postgres minimum storage is 20 GiB.
      allocatedStorage: 20,
      // gp3 = general-purpose SSD for standard OLTP workloads.
      storageType: "gp3",
      dbName: "rpg_encounters",
      username: props.dbUsername,
      password: props.dbPassword,
      dbSubnetGroupName: dbSubnetGroup.name,
      vpcSecurityGroupIds: [dbSg.id],
      publiclyAccessible: false,
      multiAz: false,
      storageEncrypted: true,
      // Keep a 3-day automated backup/PITR window.
      backupRetentionPeriod: 3,
      autoMinorVersionUpgrade: true,
      // Prevent accidental deletion from console/terraform mistakes.
      deletionProtection: true,
      skipFinalSnapshot: false,
      finalSnapshotIdentifier: `${props.resourcePrefix}-postgres-final`,
      copyTagsToSnapshot: true,
      tags: {
        service: "rpg-encounters",
        component: "database",
      },
    });

    new TerraformOutput(this, "rdsEndpoint", {
      value: db.address,
      description: "RDS endpoint host",
    });

    this.endpointHost = db.address;
  }

  get endpoint(): string {
    return this.endpointHost;
  }
}
