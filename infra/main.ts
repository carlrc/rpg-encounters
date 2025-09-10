import { Construct } from "constructs";
import { App, TerraformStack, S3Backend, TerraformAsset, Fn, TerraformOutput } from "cdktf";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import { S3BucketWebsiteConfiguration } from "@cdktf/provider-aws/lib/s3-bucket-website-configuration";
import { S3Bucket } from "@cdktf/provider-aws/lib/s3-bucket";
import { globSync } from "fs";
import { S3Object } from "@cdktf/provider-aws/lib/s3-object";
import { lookup as mime } from "mime-types";
import path from "path";
import { S3BucketPolicy } from "@cdktf/provider-aws/lib/s3-bucket-policy";
import { Vpc } from "./.gen/modules/vpc";
import { SecurityGroup } from "@cdktf/provider-aws/lib/security-group";
import { IamRole } from "@cdktf/provider-aws/lib/iam-role";
import { IamRolePolicyAttachment } from "@cdktf/provider-aws/lib/iam-role-policy-attachment";
import { IamInstanceProfile } from "@cdktf/provider-aws/lib/iam-instance-profile";
import { DataAwsAmi } from "@cdktf/provider-aws/lib/data-aws-ami";
import { Instance } from "@cdktf/provider-aws/lib/instance";
import { VolumeAttachment } from "@cdktf/provider-aws/lib/volume-attachment";
import { EbsVolume } from "@cdktf/provider-aws/lib/ebs-volume";
import { CloudfrontDistribution } from "@cdktf/provider-aws/lib/cloudfront-distribution";

const S3_ORIGIN_ID = "s3Origin";
const BACKEND_ORIGIN_ID = "backendOrigin";
const REGION = "eu-central-1";
const WHITE_LIST_COUNTRIES = [
  // North America
  "US", "CA",

  // Western Europe
  "GB", "IE", "FR", "DE", "NL", "BE", "LU", "CH", "AT", "IT", "ES", "PT",

  // Nordics
  "NO", "SE", "DK", "FI", "IS",

  // Oceania
  "AU", "NZ"
]

class PublicS3Bucket extends Construct {
  bucket: S3Bucket;

  constructor(scope: Construct, resource_prefix: string, absoluteContentPath: string) {
    super(scope, resource_prefix);
    // Get built context into the terraform context
    const { path: contentPath, assetHash: contentHash } = new TerraformAsset(
      this,
      `context`,
      {
        path: absoluteContentPath,
      }
    );

    this.bucket = new S3Bucket(this, `bucket`, {
      bucketPrefix: `${resource_prefix}`,
    });

    // Enable website delivery
    new S3BucketWebsiteConfiguration(this, `website-configuration`, {
      bucket: this.bucket.bucket,

      indexDocument: {
        suffix: "index.html",
      }
    });

    // Get all build files synchronously
    const files = globSync("**/*.{json,js,html,png,ico,txt,map,css}", {
      cwd: absoluteContentPath,
    });

    files.forEach((f) => {
      // Construct the local path to the file
      const filePath = path.join(contentPath, f);

      // Creates all the files in the bucket
      new S3Object(this, `${resource_prefix}/${f}/${contentHash}`, {
        bucket: this.bucket.id,
        key: f,
        source: filePath,
        // mime is an open source node.js tool to get mime types per extension
        contentType: mime(path.extname(f)) || "text/html",
        etag: `filemd5("${filePath}")`,
      });
    });

    // TODO: Make sure this is correct
    // allow read access to all elements within the S3Bucket
    new S3BucketPolicy(this, `s3-policy`, {
      bucket: this.bucket.id,
      policy: JSON.stringify({
        Version: "2012-10-17",
        Id: `${resource_prefix}-public-website`,
        Statement: [
          {
            Sid: "PublicRead",
            Effect: "Allow",
            Principal: "*",
            Action: ["s3:GetObject"],
            Resource: [`${this.bucket.arn}/*`, `${this.bucket.arn}`],
          },
        ],
      }),
    });
  }

  get websiteEndpoint() {
    return this.bucket.websiteEndpoint;
  }
}


class EncountersApplicationStack extends TerraformStack {
  constructor(scope: Construct, id: string, env: string) {
    super(scope, id);

    const resource_prefix = `encounters-${env}`

    new AwsProvider(this, "aws", {
      region: REGION,
    });

    new S3Backend(this, {
      bucket: `${resource_prefix}-state`,
      key: "terraform.tfstate",
    });

    // -------- VPC (public subnets) and Security Group ----------
    const vpc = new Vpc(this, "vpc", {
      name: `${resource_prefix}-public`,
      cidr: "10.0.0.0/16",
      publicSubnets: ["10.0.101.0/24", "10.0.102.0/24"],
      enableNatGateway: false,
    });

    const ec2Sg = new SecurityGroup(this, "ec2-sg", {
      name: `${resource_prefix}-public`,
      vpcId: Fn.tostring(vpc.vpcIdOutput),
      // TODO: Review these port mappings assuming https
      // TODO: Should ssh be allowed at all? Is there an AWS service which we can leverage instead for that? 
      ingress: [
        { fromPort: 80, toPort: 80, protocol: "TCP", cidrBlocks: ["0.0.0.0/0"] },
        // optional SSH. Remove if not needed.
        // { fromPort: 22, toPort: 22, protocol: "TCP", cidrBlocks: ["0.0.0.0/0"] },
      ],
      egress: [
        { fromPort: 0, toPort: 0, protocol: "-1", cidrBlocks: ["0.0.0.0/0"] },
      ],
    });

    // -------- IAM for EC2 ----------
    const role = new IamRole(this, "ec2-role", {
      name: `${resource_prefix}-ec2-role`,
      assumeRolePolicy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [{ Effect: "Allow", Principal: { Service: "ec2.amazonaws.com" }, Action: "sts:AssumeRole" }],
      }),
      inlinePolicy: [
        {
          name: "basic",
          policy: JSON.stringify({
            Version: "2012-10-17",
            Statement: [
              { Effect: "Allow", Action: ["ssm:UpdateInstanceInformation"], Resource: "*" },
            ],
          }),
        },
      ],
    });

    new IamRolePolicyAttachment(this, "ec2-ecr-ro", {
      role: role.name,
      policyArn: "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    });

    const instanceProfile = new IamInstanceProfile(this, "ec2-profile", {
      name: `${resource_prefix}-backend`,
      role: role.name,
    });

    // TODO: verify this isn't taking an outdated image should be latest
    // -------- AMI (Amazon Linux 2023) ----------
    const ami = new DataAwsAmi(this, "al2023", {
      mostRecent: true,
      owners: ["137112412989"], // Amazon
      filter: [
        { name: "name", values: ["al2023-ami-*-x86_64"] },
        { name: "architecture", values: ["x86_64"] },
      ],
    });

    // -------- 20 GiB EBS for Postgres data ----------
    const dbVolume = new EbsVolume(this, "db-ebs", {
      availabilityZone: `${REGION}a`,
      size: 20,
      type: "gp3",
      tags: { purpose: "postgres-data" },
    });

    // -------- EC2 instance (t3.medium) ----------
    const ec2 = new Instance(this, "app-ec2", {
      ami: ami.id,
      instanceType: "t3.medium",
      associatePublicIpAddress: true,
      subnetId: Fn.element(Fn.tolist(vpc.publicSubnetsOutput), 0),
      vpcSecurityGroupIds: [ec2Sg.id],
      iamInstanceProfile: instanceProfile.name,
      // TODO: a user script should be setup somewhere else and imported here
      userData: "",
    });

    new VolumeAttachment(this, "db-attach", {
      deviceName: "/dev/sdf", // appears as /dev/xvdf
      instanceId: ec2.id,
      volumeId: dbVolume.id,
      skipDestroy: false,
    });

    // -------- Frontend S3 + CloudFront ----------
    const frontend = new PublicS3Bucket(
      this,
      `${resource_prefix}-frontend`,
      path.resolve(__dirname, "../frontend/dist")
    );

    // TODO: Setup route 53 hosted zone assuming SSM '/dns/root-domain/hosted-zone-id'
    // TODO: Setup route 53 root domain assuming SSM '/dns/root-domain'

    const cdn = new CloudfrontDistribution(this, "cdn", {
      enabled: true,
      comment: "Frontend via S3, backend via EC2",
      defaultRootObject: "index.html",
      defaultCacheBehavior: {
        allowedMethods: ["GET", "HEAD", "OPTIONS"],
        cachedMethods: ["GET", "HEAD"],
        targetOriginId: S3_ORIGIN_ID,
        viewerProtocolPolicy: "redirect-to-https",
        // TODO: Pretty sure we need to forward cookies for session cookies?
        forwardedValues: { queryString: true, cookies: { forward: "none" } },
      },
      orderedCacheBehavior: [
        {
          // TODO: review this assuming caddy is setup
          pathPattern: "/backend/*",
          targetOriginId: BACKEND_ORIGIN_ID,
          allowedMethods: ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
          cachedMethods: ["GET", "HEAD"],
          viewerProtocolPolicy: "redirect-to-https",
          minTtl: 0,
          defaultTtl: 10,
          maxTtl: 50,
          forwardedValues: {
            queryString: true,
            headers: ["*"],
            cookies: { forward: "all" },
          },
        },
      ],
      // TODO: update to https only assuming Caddy setup on EC2
      origin: [
        {
          originId: S3_ORIGIN_ID,
          domainName: frontend.websiteEndpoint,
          customOriginConfig: {
            originProtocolPolicy: "https-only",
            httpPort: 80,
            httpsPort: 443,
            originSslProtocols: ["TLSv1.2"],
          },
        },
        {
          originId: BACKEND_ORIGIN_ID,
          domainName: ec2.publicDns,
          customOriginConfig: {
            originProtocolPolicy: "http-only",
            httpPort: 80,
            httpsPort: 443,
            originSslProtocols: ["TLSv1.2"],
          },
        },
      ],
      restrictions: { geoRestriction: { restrictionType: "whitelist", locations: WHITE_LIST_COUNTRIES } },
      viewerCertificate: { cloudfrontDefaultCertificate: true },
    });

    new TerraformOutput(this, "domainName", {
      value: cdn.domainName,
    });
  }
}

const app = new App();
new EncountersApplicationStack(app, "encounters-app", "prd");

app.synth();
