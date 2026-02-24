import { App, TerraformStack, TerraformOutput } from "cdktf";
import * as dotenv from "dotenv";
import * as path from "path";
import { Construct } from "constructs";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import { S3Bucket } from "@cdktf/provider-aws/lib/s3-bucket";
import { EncountersApplicationStack } from "./stacks/applicaton-stack";
import { DnsStack } from "./stacks/dns-stack";
import { DbStack } from "./stacks/db-stack";

const REGION = "eu-central-1";
const DNS_ROLE_ARN =
  "arn:aws:iam::833083742566:role/domain-rpg-encounters.com-route53-update";
dotenv.config({ path: path.resolve(__dirname, ".env"), quiet: true });

class EncountersBootstrapStack extends TerraformStack {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    const resource_prefix = `rpg-encounters`;

    new AwsProvider(this, "aws-default", {
      region: REGION,
    });

    // Create S3 bucket for Terraform state
    const stateBucket = new S3Bucket(this, "state-bucket", {
      bucket: `${resource_prefix}-state`,
    });

    new TerraformOutput(this, "stateBucketName", {
      value: stateBucket.bucket,
    });
  }
}

const dbUsername = process.env.POSTGRES_USER;
const dbPassword = process.env.POSTGRES_PASSWORD;
if (!dbUsername || !dbPassword) {
  throw new Error("Missing POSTGRES_USER or POSTGRES_PASSWORD in .env.");
}

const app = new App();
new EncountersBootstrapStack(app, "rpg-encounters-bootstrap");
const appStack = new EncountersApplicationStack(app, "rpg-encounters-app", {
  region: REGION,
  stateBucketName: "rpg-encounters-state",
});
new DbStack(app, "rpg-encounters-db", {
  region: REGION,
  stateBucketName: "rpg-encounters-state",
  resourcePrefix: "rpg-encounters",
  vpcId: appStack.vpcId,
  subnetIds: appStack.publicSubnetIds,
  ec2SecurityGroupId: appStack.ec2SecurityGroupId,
  dbUsername,
  dbPassword,
});
new DnsStack(app, "rpg-encounters-dns", {
  region: REGION,
  stateBucketName: "rpg-encounters-state",
  dnsRoleArn: DNS_ROLE_ARN,
  rootDomain: appStack.rootDomainValue,
  hostedZoneId: appStack.hostedZoneIdValue,
  cloudFrontDomainName: appStack.cloudFrontDomainName,
});

app.synth();
