# Cloud Migration

Domain-specific discovery for on-prem to cloud.

## Motivation
- Why cloud?
- Business case?
- Timeline pressure?
- Which provider? Why?

## Current State
- How many apps?
- What technologies?
- Application dependencies?
- How many VMs?
- Total compute/storage?
- Database platforms?

## Migration Strategy (6Rs)
- **Rehost** (lift-shift): Which apps?
- **Replatform**: Which need minor mods?
- **Refactor**: Which need re-arch?
- **Retire**: What can we decommission?
- **Retain**: What stays on-prem?
- **Repurchase**: Replace with SaaS?

## Wave Planning
- What's wave 1?
- Sequencing: easy-first or hard-first?
- Dependencies between waves?
- Cutover approach?

## Architecture

### Compute
- VM sizing?
- Auto-scaling?
- Spot/reserved instances?
- Container strategy?

### Networking
- VPC design?
- Hybrid connectivity?
- Bandwidth requirements?
- Latency tolerance?

### Storage
- Storage tiers?
- IOPS requirements?
- Backup strategy?

### Database
- Managed or self-managed?
- Multi-AZ?
- Migration method?
- Downtime tolerance?

## Security
- SSO? MFA?
- Firewall rules?
- VPN or private link?
- Encryption at rest/transit?
- Key management?
- Compliance frameworks?

## Cost
- Current on-prem cost?
- Expected cloud cost?
- TCO comparison?
- Right-sizing strategy?
- Reserved capacity?
- Data egress modeled?

## Execution
- Migration tools?
- Testing strategy?
- Cutover window?
- Go/no-go criteria?
- Rollback triggers?

## Operations
- Who operates cloud?
- 24/7 support?
- FinOps process?
- Optimization cadence?

## Pitfalls
- Underestimating dependencies
- Ignoring network latency
- Not modeling egress costs
- Over-provisioning
- Insufficient testing
- No rollback plan

## Red Flags
- "Lift-and-shift everything"
- "Cloud is always cheaper"
- "We'll figure out network later"
- "Security doesn't need involvement yet"
- "We don't need a pilot"
