import { Construct } from "constructs";
import { App, TerraformStack, S3Backend, TerraformAsset, Fn, TerraformOutput } from "cdktf";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import { S3BucketWebsiteConfiguration } from "@cdktf/provider-aws/lib/s3-bucket-website-configuration";
import { S3Bucket } from "@cdktf/provider-aws/lib/s3-bucket";
import { globSync } from "fs";
import { S3Object } from "@cdktf/provider-aws/lib/s3-object";
import { lookup as mime } from "mime-types";
import path from "path";
import * as fs from "fs";
import { S3BucketPolicy } from "@cdktf/provider-aws/lib/s3-bucket-policy";
import { Vpc } from "./.gen/modules/vpc";
import { SecurityGroup } from "@cdktf/provider-aws/lib/security-group";
import { IamRole } from "@cdktf/provider-aws/lib/iam-role";
import { IamRolePolicyAttachment } from "@cdktf/provider-aws/lib/iam-role-policy-attachment";
import { IamInstanceProfile } from "@cdktf/provider-aws/lib/iam-instance-profile";
import { DataAwsAmi } from "@cdktf/provider-aws/lib/data-aws-ami";
import { Instance } from "@cdktf/provider-aws/lib/instance";
import { LaunchTemplate } from "@cdktf/provider-aws/lib/launch-template";
import { VolumeAttachment } from "@cdktf/provider-aws/lib/volume-attachment";
import { EbsVolume } from "@cdktf/provider-aws/lib/ebs-volume";
import { CloudfrontDistribution } from "@cdktf/provider-aws/lib/cloudfront-distribution";
import { DataAwsSsmParameter } from "@cdktf/provider-aws/lib/data-aws-ssm-parameter"import { Route53Record } from "@cdktf/provider-aws/lib/route53-record";
import { AcmCertificate } from "@cdktf/provider-aws/lib/acm-certificate";
import { AcmCertificateValidation } from "@cdktf/provider-aws/lib/acm-certificate-validation";

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

    // Allow read access to all elements within the S3Bucket
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

    new AwsProvider(this, "aws-default", {
      alias: "default",
      region: REGION,
    });

    // ACM certificates for CloudFront
    const usEast1Provider = new AwsProvider(this, "aws-us-east-1", {
      alias: "acm-provider",
      region: "us-east-1",
    });

    new S3Backend(this, {
      bucket: `${resource_prefix}-state`,
      key: "terraform.tfstate",
    });

    // -------- VPC (public subnets) and Security Group ----------
    const vpc = new Vpc(this, "vpc", {
      name: `${resource_prefix}-public`,
      cidr: "10.0.0.0/16",
      publicSubnets: ["10.0.101.0/24"],
      enableNatGateway: false,
    });

    const ec2Sg = new SecurityGroup(this, "ec2-sg", {
      name: `${resource_prefix}-public`,
      vpcId: vpc.vpcIdOutput,
      // Use AWS System Manager for SSH don't open ports
      ingress: [
        { fromPort: 80, toPort: 80, protocol: "TCP", cidrBlocks: ["0.0.0.0/0"] },
        { fromPort: 443, toPort: 443, protocol: "TCP", cidrBlocks: ["0.0.0.0/0"] },
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

    // -------- AMI (Amazon Linux 2023) ----------
    const ami = new DataAwsAmi(this, "al2023", {
      mostRecent: true,
      owners: ["137112412989"], // Amazon
      filter: [
        { name: "name", values: ["al2023-ami-*-x86_64"] },
        { name: "architecture", values: ["x86_64"] },
      ],
    });

    // -------- EBS for Postgres data ----------
    const dbVolume = new EbsVolume(this, "db-ebs", {
      availabilityZone: `${REGION}a`,
      size: 20,
      type: "gp3",
      tags: { purpose: "postgres-data" },
    });

    // -------- Docker Compose Asset ----------
    const composeAsset = new TerraformAsset(this, "docker-compose", {
      path: path.resolve(__dirname, "../backend/docker-compose.yml")
    });

    // -------- EC2 instance ----------
    // Read .env.production file and embed in user data
    const envContent = fs.readFileSync(path.resolve(__dirname, "../backend/.env.production"), "utf8");
    const userDataScript = fs.readFileSync(path.resolve(__dirname, "scripts/user-data.sh"), "utf8")
      .replace("{{ENV_CONTENT}}", Buffer.from(envContent).toString('base64'))
      .replace("{{COMPOSE_PATH}}", composeAsset.path);

    // -------- Launch Template ----------
    const launchTemplate = new LaunchTemplate(this, "backend-lt", {
      name: `${resource_prefix}-backend`,
      imageId: ami.id,
      instanceType: "t3.large",
      iamInstanceProfile: {
        arn: instanceProfile.arn
      },
      vpcSecurityGroupIds: [ec2Sg.id],
      userData: Fn.base64encode(userDataScript),
    });

    const ec2 = new Instance(this, "app-ec2", {
      launchTemplate: {
        id: launchTemplate.id,
        version: "$Latest"
      },
      associatePublicIpAddress: true,
      subnetId: vpc.publicSubnetsOutput,
      vpcSecurityGroupIds: [ec2Sg.id],
      iamInstanceProfile: instanceProfile.name,
      userData: Fn.base64encode(userDataScript),
    });

    new VolumeAttachment(this, "db-attach", {
      // appears as /dev/xvdf
      deviceName: "/dev/sdf",
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

    // -------- Route 53 Setup ----------
    // Get hosted zone ID and root domain from SSM Parameter Store
    const hostedZoneId = new DataAwsSsmParameter(this, "hosted-zone-id", {
      name: "/dns/root-domain/hosted-zone-id",
    });

    const rootDomain = new DataAwsSsmParameter(this, "root-domain", {
      name: "/dns/root-domain",
    });

    // -------- ACM Certificate (US East 1 for CloudFront) ----------
    const sslCertificate = new AcmCertificate(this, "ssl-certificate", {
      provider: usEast1Provider,
      domainName: rootDomain.value,
      validationMethod: "DNS",
      lifecycle: {
        createBeforeDestroy: true,
      },
    });

    // Wait for certificate validation (CDKTF will automatically create validation records)
    const certValidation = new AcmCertificateValidation(this, "cert-validation", {
      provider: usEast1Provider,
      certificateArn: sslCertificate.arn,
    });

    const cdn = new CloudfrontDistribution(this, "cdn", {
      enabled: true,
      comment: "Frontend via S3, backend via EC2",
      defaultRootObject: "index.html",
      aliases: [rootDomain.value],
      defaultCacheBehavior: {
        allowedMethods: ["GET", "HEAD", "OPTIONS"],
        cachedMethods: ["GET", "HEAD"],
        targetOriginId: S3_ORIGIN_ID,
        viewerProtocolPolicy: "redirect-to-https",
        forwardedValues: { queryString: true, cookies: { forward: "none" } },
      },
      orderedCacheBehavior: [
        {
          pathPattern: "/api/*",
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
      origin: [
        {
          originId: S3_ORIGIN_ID,
          domainName: frontend.websiteEndpoint,
          customOriginConfig: {
            // S3 website endpoints only support HTTP
            originProtocolPolicy: "http-only",
            httpPort: 80,
            httpsPort: 443,
            originSslProtocols: ["TLSv1.2"],
          },
        },
        {
          originId: BACKEND_ORIGIN_ID,
          domainName: ec2.publicDns,
          customOriginConfig: {
            // Backend now serves HTTPS via Caddy
            originProtocolPolicy: "https-only",
            httpPort: 80,
            httpsPort: 443,
            originSslProtocols: ["TLSv1.2"],
          },
        },
      ],
      restrictions: { geoRestriction: { restrictionType: "whitelist", locations: WHITE_LIST_COUNTRIES } },
      viewerCertificate: {
        acmCertificateArn: certValidation.certificateArn,
        sslSupportMethod: "sni-only",
        minimumProtocolVersion: "TLSv1.2_2021",
      },
    });

    // -------- Route 53 DNS Record ----------
    // Create A record pointing to CloudFront distribution
    new Route53Record(this, "root-domain-record", {
      zoneId: hostedZoneId.value,
      name: rootDomain.value,
      type: "A",
      alias: {
        name: cdn.domainName,
        zoneId: cdn.hostedZoneId,
        evaluateTargetHealth: false,
      },
    });

    // Create AAAA record (IPv6) pointing to CloudFront distribution
    new Route53Record(this, "root-domain-record-ipv6", {
      zoneId: hostedZoneId.value,
      name: rootDomain.value,
      type: "AAAA",
      alias: {
        name: cdn.domainName,
        zoneId: cdn.hostedZoneId,
        evaluateTargetHealth: false,
      },
    });

    new TerraformOutput(this, "domainName", {
      value: cdn.domainName,
    });

    new TerraformOutput(this, "customDomain", {
      value: rootDomain.value,
    });
  }
}

const app = new App();
new EncountersApplicationStack(app, "encounters-app", "prd");

app.synth();
