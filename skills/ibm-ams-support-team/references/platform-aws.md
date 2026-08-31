# AWS — Platform Reference

## Resolver Scope

EC2, ECS, EKS, Lambda, Fargate, S3, EBS, EFS, RDS, DynamoDB, Aurora, Redshift, VPC, Route 53, CloudFront, ALB/NLB, IAM, KMS, Secrets Manager, Security Hub, GuardDuty, WAF, CloudWatch, CloudTrail, X-Ray, SQS, SNS, EventBridge, Step Functions, Cost Explorer.

## Triage Signals

| Signal | Likely Category | Initial Action |
|--------|----------------|----------------|
| "Instance unreachable" | Compute / Network | Check instance status checks, security groups, NACLs, route tables |
| "AccessDenied", "403" | IAM / Permissions | Review IAM policy, resource policy, SCP, trust relationships |
| "5xx errors" | Application / Infra | Check ALB target health, application logs, Auto Scaling events |
| "High latency" | Performance | Check CloudWatch metrics, X-Ray traces, DB connection pool |
| "Disk full", "Storage limit" | Storage | Check EBS volume usage, S3 bucket policies, lifecycle rules |
| "Lambda timeout" | Compute / Config | Check timeout setting, memory allocation, cold start patterns |
| "Cannot connect to RDS" | Database / Network | Check security groups, subnet routing, parameter group, storage |
| "Billing spike" | Cost | Check Cost Explorer, identify unused resources, Reserved Instance coverage |
| "Deployment failed" | Change / Pipeline | Check CodePipeline/CodeDeploy logs, IAM roles, resource limits |

## Investigation Checklist

1. Identify the AWS account and region
2. Check AWS Health Dashboard for service-wide issues
3. Review CloudTrail for recent API calls and config changes
4. Check CloudWatch alarms and metrics for the affected service
5. Review VPC Flow Logs for network-level issues
6. Check IAM Access Analyzer for permission issues
7. Review AWS Config for configuration compliance and drift

## Common Resolutions

**Permission issues:** Correct IAM policy (least privilege), update resource policy, check SCP inheritance.
**Instance issues:** Reboot/replace instance, check status checks, verify AMI, review Auto Scaling.
**Network issues:** Fix security group rules, correct route table entries, verify NACL order.
**Database issues:** Check storage auto-scaling, review slow query log, verify parameter group settings.
**Cost issues:** Identify and terminate unused resources, right-size instances, purchase Reserved Instances/Savings Plans.

## Vendor Escalation (AWS Support)

Portal: AWS Support Console (requires Business or Enterprise support plan)
Required information: Account ID, Region, Resource ARN(s), CloudTrail event IDs, CloudWatch metric screenshots, reproduction steps.

Severity mapping:
| AWS | IBM |
|-----|-----|
| Critical (production down) | P1 |
| Urgent (production impaired) | P2 |
| High (important) | P3 |
| Low (general guidance) | P4 |

For Enterprise accounts, contact the Technical Account Manager (TAM) directly for P1/P2 issues.
