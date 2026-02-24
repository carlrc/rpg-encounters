import { Construct } from "constructs";
import { S3Backend, TerraformStack } from "cdktf";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import { Route53Record } from "@cdktf/provider-aws/lib/route53-record";

// AWS-managed hosted zone ID used by all CloudFront distributions for Route53 ALIAS records.
const CLOUDFRONT_HOSTED_ZONE_ID = "Z2FDTNDATAQYW2";

type DnsStackProps = {
  region: string;
  stateBucketName: string;
  dnsRoleArn: string;
  rootDomain: string;
  hostedZoneId: string;
  cloudFrontDomainName: string;
};

export class DnsStack extends TerraformStack {
  constructor(scope: Construct, id: string, props: DnsStackProps) {
    super(scope, id);

    new S3Backend(this, {
      bucket: props.stateBucketName,
      key: "dns/prd/terraform.tfstate",
      region: props.region,
    });

    const dnsAccountProvider = new AwsProvider(this, "aws-dns", {
      region: props.region,
      assumeRole: [
        {
          roleArn: props.dnsRoleArn,
        },
      ],
    });

    new Route53Record(this, "a-record", {
      zoneId: props.hostedZoneId,
      name: props.rootDomain,
      type: "A",
      alias: {
        name: props.cloudFrontDomainName,
        // CloudFront distributions always use this hosted zone ID for ALIAS records
        zoneId: CLOUDFRONT_HOSTED_ZONE_ID,
        evaluateTargetHealth: false,
      },
      provider: dnsAccountProvider,
    });
  }
}
