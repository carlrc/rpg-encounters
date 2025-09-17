import { Construct } from "constructs";
import { App, TerraformStack, S3Backend, TerraformAsset, TerraformOutput, Fn } from "cdktf";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import { S3BucketWebsiteConfiguration } from "@cdktf/provider-aws/lib/s3-bucket-website-configuration";
import { S3Bucket } from "@cdktf/provider-aws/lib/s3-bucket";
import { globSync } from "fs";
import { S3Object } from "@cdktf/provider-aws/lib/s3-object";
import { lookup as mime } from "mime-types";
import * as path from "path";
import * as fs from "fs";
import { execSync } from "child_process";
import { S3BucketPolicy } from "@cdktf/provider-aws/lib/s3-bucket-policy";
import { S3BucketPublicAccessBlock } from "@cdktf/provider-aws/lib/s3-bucket-public-access-block";
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
import { DataAwsSsmParameter } from "@cdktf/provider-aws/lib/data-aws-ssm-parameter";
import { Route53Record } from "@cdktf/provider-aws/lib/route53-record";
import { Lb } from "@cdktf/provider-aws/lib/lb";
import { LbTargetGroup } from "@cdktf/provider-aws/lib/lb-target-group";
import { LbListener } from "@cdktf/provider-aws/lib/lb-listener";
import { LbTargetGroupAttachment } from "@cdktf/provider-aws/lib/lb-target-group-attachment";

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
  websiteConfig: S3BucketWebsiteConfiguration;

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

    // Configure public access block settings for static website
    const publicAccessBlock = new S3BucketPublicAccessBlock(this, `public-access-block`, {
      bucket: this.bucket.id,
      blockPublicAcls: true,
      blockPublicPolicy: false, // Allow public bucket policy
      ignorePublicAcls: true,
      restrictPublicBuckets: false, // Allow public access for static website
    });

    // Enable website delivery
    this.websiteConfig = new S3BucketWebsiteConfiguration(this, `website-configuration`, {
      bucket: this.bucket.bucket,

      indexDocument: {
        suffix: "index.html",
      },
      errorDocument: {
        key: "index.html",
      }
    });

    // Get all build files synchronously
    const files = globSync("**/*.{json,js,html,png,ico,txt,map,css,md}", {
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
        serverSideEncryption: "AES256"
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
      dependsOn: [publicAccessBlock],
    });
  }

  get websiteEndpoint() {
    return this.websiteConfig.websiteEndpoint;
  }
}


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

class EncountersApplicationStack extends TerraformStack {
  private hostedZoneId: string;
  private rootDomain: string;
  private ec2PublicIps: string[];
  private cdnDomainName: string;

  constructor(scope: Construct, id: string, env: string) {
    super(scope, id);

    const resource_prefix = `encounters-${env}`

    new AwsProvider(this, "aws-default", {
      alias: "default",
      region: REGION,
    });

    const stateBucketName = `rpg-encounters-state`
    // Use S3 backend for state storage
    new S3Backend(this, {
      bucket: stateBucketName,
      key: "terraform.tfstate",
      region: REGION,
    });

    // -------- VPC (public subnets) and Security Group ----------
    const vpc = new Vpc(this, "vpc", {
      name: `${resource_prefix}-public`,
      cidr: "10.0.0.0/16",
      azs: ["eu-central-1a", "eu-central-1b"],
      publicSubnets: ["10.0.101.0/24", "10.0.102.0/24"],
      enableNatGateway: false,
      enableDnsHostnames: true,
      enableDnsSupport: true,
      createIgw: true,
      mapPublicIpOnLaunch: true,

    });

    // ALB Security Group - allows HTTP/HTTPS from internet
    const albSg = new SecurityGroup(this, "alb-sg", {
      name: `${resource_prefix}-alb`,
      vpcId: vpc.vpcIdOutput,
      ingress: [
        { fromPort: 80, toPort: 80, protocol: "TCP", cidrBlocks: ["0.0.0.0/0"] },
        { fromPort: 443, toPort: 443, protocol: "TCP", cidrBlocks: ["0.0.0.0/0"] },
      ],
      egress: [
        { fromPort: 0, toPort: 0, protocol: "-1", cidrBlocks: ["0.0.0.0/0"] },
      ],
    });

    // EC2 Security Group - allows port 8000 from ALB only
    const ec2Sg = new SecurityGroup(this, "ec2-sg", {
      name: `${resource_prefix}-ec2`,
      vpcId: vpc.vpcIdOutput,
      // Use AWS System Manager for SSH don't open ports
      ingress: [
        { fromPort: 8000, toPort: 8000, protocol: "TCP", securityGroups: [albSg.id] },
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
              { Effect: "Allow", Action: ["s3:GetObject"], Resource: `arn:aws:s3:::${stateBucketName}/*` },
              {
                Effect: "Allow",
                Action: [
                  "ses:SendEmail",
                  "ses:SendRawEmail",
                  "ses:GetSendQuota",
                  "ses:GetSendStatistics"
                ],
                Resource: "*"
              },
            ],
          }),
        },
      ],
    });

    new IamRolePolicyAttachment(this, "ec2-ecr-ro", {
      role: role.name,
      policyArn: "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    });

    new IamRolePolicyAttachment(this, "ec2-ssm-core", {
      role: role.name,
      policyArn: "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
    });

    const instanceProfile = new IamInstanceProfile(this, "ec2-profile", {
      namePrefix: `${resource_prefix}-backend-`,
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
      encrypted: true,
      tags: { purpose: "postgres-data" },
    });

    // -------- Upload config files to S3 for instance access ----------
    new S3Object(this, "docker-compose-config", {
      bucket: stateBucketName,
      key: "docker-compose.yml",
      source: path.resolve(__dirname, "../backend/docker-compose.yml"),
      contentType: "text/yaml"
    });


    new S3Object(this, "env-config", {
      bucket: stateBucketName,
      key: ".env.production",
      source: path.resolve(__dirname, "../backend/.env.production"),
      contentType: "text/plain"
    });

    // -------- Route 53 Setup ----------
    const rootDomain = new DataAwsSsmParameter(this, "root-domain", {
      name: "/dns/root-domain",
    });

    // Use existing hosted zone for the domain (in DNS account)
    const hostedZoneId = new DataAwsSsmParameter(this, "root-domain-hosted-zone", {
      name: "/dns/root-domain/hosted-zone-id",
    });

    // -------- Application Load Balancer ----------
    // -------- ACM Certificate (EU Central 1 for ALB) ----------
    const albSslCertificateArn = "arn:aws:acm:eu-central-1:248190630760:certificate/79db36ae-801c-4b8b-ba9d-21aae8241ca3"
    const alb = new Lb(this, "alb", {
      name: `${resource_prefix}-alb`,
      loadBalancerType: "application",
      internal: false,
      securityGroups: [albSg.id],
      subnets: Fn.tolist(vpc.publicSubnetsOutput),
      enableDeletionProtection: false,
    });

    const targetGroup = new LbTargetGroup(this, "alb-tg", {
      name: `${resource_prefix}-tg`,
      port: 8000,
      protocol: "HTTP",
      vpcId: vpc.vpcIdOutput,
      targetType: "instance",
      healthCheck: {
        enabled: true,
        healthyThreshold: 2,
        unhealthyThreshold: 2,
        timeout: 5,
        interval: 30,
        path: "/api/health",
        matcher: "200",
        port: "traffic-port",
        protocol: "HTTP",
      },
    });

    // HTTPS Listener
    new LbListener(this, "alb-https-listener", {
      loadBalancerArn: alb.arn,
      port: 443,
      protocol: "HTTPS",
      sslPolicy: "ELBSecurityPolicy-TLS-1-2-2017-01",
      certificateArn: albSslCertificateArn,
      defaultAction: [{
        type: "forward",
        targetGroupArn: targetGroup.arn,
      }],
    });

    // HTTP Listener (redirect to HTTPS)
    new LbListener(this, "alb-http-listener", {
      loadBalancerArn: alb.arn,
      port: 80,
      protocol: "HTTP",
      defaultAction: [{
        type: "redirect",
        redirect: {
          port: "443",
          protocol: "HTTPS",
          statusCode: "HTTP_301",
        },
      }],
    });

    // https://instances.vantage.sh/
    // -------- EC2 instance ----------
    const launchTemplate = new LaunchTemplate(this, "backend-lt", {
      name: `${resource_prefix}-backend`,
      imageId: ami.id,
      instanceType: "c7a.xlarge",
      iamInstanceProfile: {
        arn: instanceProfile.arn
      },
      blockDeviceMappings: [{
        deviceName: "/dev/xvda",
        ebs: {
          volumeSize: 10,
          volumeType: "gp3",
          encrypted: "true",
          deleteOnTermination: "true",
        }
      }],
      networkInterfaces: [{
        associatePublicIpAddress: "true",
        subnetId: Fn.element(vpc.publicSubnetsOutput, 0),
        securityGroups: [ec2Sg.id],
        deviceIndex: 0,
      }],
    });

    const ec2 = new Instance(this, "app-ec2", {
      launchTemplate: {
        id: launchTemplate.id,
        version: "$Latest"
      },
    });

    // -------- EBS ----------
    new VolumeAttachment(this, "db-attach", {
      // appears as /dev/xvdf
      deviceName: "/dev/sdf",
      instanceId: ec2.id,
      volumeId: dbVolume.id,
      skipDestroy: false,
    });

    // Attach EC2 instance to ALB target group
    new LbTargetGroupAttachment(this, "alb-tg-attachment", {
      targetGroupArn: targetGroup.arn,
      targetId: ec2.id,
      port: 8000,
    });


    // -------- Frontend S3 + CloudFront ----------
    const frontend = new PublicS3Bucket(
      this,
      `${resource_prefix}-frontend`,
      path.resolve(__dirname, "../frontend/dist")
    );


    // -------- ACM Certificate (US East 1 for CloudFront) ----------
    // ****IMPORTANT****: Certificate manually created in RPG Account and imported into DNS account as CNAME record
    const cloudFrontSslCertificateArn = "arn:aws:acm:us-east-1:248190630760:certificate/7bc847d1-c196-41db-b44b-4268a5f79bd2";

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
          domainName: alb.dnsName,
          customOriginConfig: {
            // Backend serves HTTPS via ALB
            originProtocolPolicy: "https-only",
            httpPort: 80,
            httpsPort: 443,
            originSslProtocols: ["TLSv1.2"],
          },
        },
      ],
      restrictions: { geoRestriction: { restrictionType: "whitelist", locations: WHITE_LIST_COUNTRIES } },
      customErrorResponse: [
        {
          errorCode: 404,
          responseCode: 200,
          responsePagePath: "/index.html",
          errorCachingMinTtl: 10,
        },
        {
          errorCode: 403,
          responseCode: 200,
          responsePagePath: "/index.html",
          errorCachingMinTtl: 10,
        },
      ],
      viewerCertificate: {
        acmCertificateArn: cloudFrontSslCertificateArn,
        sslSupportMethod: "sni-only",
        minimumProtocolVersion: "TLSv1.2_2021",
      },
    });

    // Prepare user data script with CloudFront domain
    const userDataScript = fs.readFileSync(path.resolve(__dirname, "scripts/user-data.sh"), "utf8")
      .replace(/\{\{STATE_BUCKET\}\}/g, stateBucketName)
      .replace(/\{\{GIT_SHA\}\}/g, execSync('git rev-parse --short HEAD', { encoding: 'utf8' }).trim())

    const userDataBase64 = Buffer.from(userDataScript).toString('base64');

    // Update EC2 instance with user data
    ec2.addOverride('user_data_base64', userDataBase64);

    new TerraformOutput(this, "domainName", {
      value: cdn.domainName,
    });

    new TerraformOutput(this, "customDomain", {
      value: rootDomain.value,
      sensitive: true,
    });

    new TerraformOutput(this, "ec2PublicIp", {
      value: ec2.publicIp,
      description: "EC2 instance public IP address",
    });

    this.rootDomain = rootDomain.value;
    this.hostedZoneId = hostedZoneId.value;
    this.ec2PublicIps = [ec2.publicIp];
    this.cdnDomainName = cdn.domainName;
  }

  get ec2PublicIp(): string[] {
    return this.ec2PublicIps;
  }

  get rootDomainValue(): string {
    return this.rootDomain;
  }

  get hostedZoneIdValue(): string {
    return this.hostedZoneId;
  }

  get cloudFrontDomainName(): string {
    return this.cdnDomainName;
  }
}

class EncountersDnsStack extends TerraformStack {
  constructor(scope: Construct, id: string, appStack: EncountersApplicationStack) {
    super(scope, id);

    const dnsAccountProvider = new AwsProvider(this, "aws-dns", {
      region: REGION,
      assumeRole: [{
        roleArn: "arn:aws:iam::833083742566:role/domain-rpg-encounters.com-route53-update"
      }],
    });

    // Create ALIAS record pointing to CloudFront distribution (using DNS account provider)
    new Route53Record(this, "a-record", {
      zoneId: appStack.hostedZoneIdValue,
      name: appStack.rootDomainValue,
      type: "A",
      alias: {
        name: appStack.cloudFrontDomainName,
        // CloudFront distributions always use this hosted zone ID for ALIAS records
        zoneId: "Z2FDTNDATAQYW2",
        evaluateTargetHealth: false,
      },
      provider: dnsAccountProvider,
    });
  }
}

const app = new App();
new EncountersBootstrapStack(app, "rpg-encounters-bootstrap");
const appStack = new EncountersApplicationStack(app, "rpg-encounters-app", "prd");
new EncountersDnsStack(app, "rpg-encounters-dns", appStack);

app.synth();
