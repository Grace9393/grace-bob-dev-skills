# Vendor Escalation Reference

## Standard Vendor Escalation Process

1. Exhaust internal investigation — confirm the issue is beyond IBM's control
2. Prepare the escalation package using the format from the escalation skill
3. Raise a case on the vendor's support portal with all required information
4. Record the vendor case ID in the ServiceNow ticket
5. Chase per the vendor's SLA — do not wait passively
6. Translate vendor updates into customer-friendly language
7. Update the KEDB with any vendor-provided workarounds

## Vendor Directory

### Salesforce

| Item | Detail |
|------|--------|
| Portal | help.salesforce.com |
| Required info | Org ID, User ID, debug logs, reproduction steps, release version |
| Sev 1 → IBM P1 | Production system down |
| Sev 2 → IBM P2 | Major feature broken |
| Sev 3 → IBM P3/P4 | Minor issue |
| SLA (Sev 1) | 1 hour initial response |
| Escalation path | Request management escalation via the case portal |

### AWS

| Item | Detail |
|------|--------|
| Portal | AWS Support Console (Business/Enterprise plan required) |
| Required info | Account ID, Region, Resource ARN(s), CloudTrail events, CloudWatch metrics |
| Critical → IBM P1 | Production system down |
| Urgent → IBM P2 | Production impaired |
| High → IBM P3 | Important, not production |
| Low → IBM P4 | General guidance |
| SLA (Critical) | 15 min initial response (Enterprise) |
| Escalation path | Contact TAM directly for Enterprise accounts; request case escalation for Business |

### Microsoft (SharePoint / M365)

| Item | Detail |
|------|--------|
| Portal | Microsoft 365 Admin Centre > Support |
| Required info | Tenant ID, site URL, user UPN, browser/OS, reproduction steps, diagnostics |
| Sev A → IBM P1 | Service down |
| Sev B → IBM P2 | Service degraded |
| Sev C → IBM P3/P4 | Non-critical |
| SLA (Sev A) | 1 hour initial response |
| Escalation path | Request escalation through the case; Premier/Unified Support for faster response |

### ServiceNow

| Item | Detail |
|------|--------|
| Portal | HI Service Portal (hi.service-now.com) |
| Required info | Instance URL, version, stats.do output, system logs, reproduction steps |
| Sev 1 → IBM P1 | Production down |
| Sev 2 → IBM P2 | Significant impact |
| Sev 3 → IBM P3 | Limited impact |
| Sev 4 → IBM P4 | Minimal impact |
| SLA (Sev 1) | 30 min initial response |
| Escalation path | Request management escalation via the case portal |

### IBM Internal (NAVI and other IBM tools)

| Item | Detail |
|------|--------|
| Portal | IBM internal support channels |
| Required info | Serial number, w3id, module affected, browser/OS, screenshots |
| Escalation path | Engage platform team directly through IBM internal ticketing |

## Chase Cadence

| Vendor Severity | Chase Frequency |
|-----------------|-----------------|
| Critical / Sev 1 | Every 2 hours |
| High / Sev 2 | Every 4 hours |
| Medium / Sev 3 | Daily |
| Low / Sev 4 | Every 3 business days |

## Escalating Within a Vendor

If the vendor's initial response is inadequate or slow:

1. Request management escalation through the case
2. Reference IBM's partnership and contract terms
3. Provide updated business impact quantification
4. Set a clear deadline with business justification
5. If still blocked, escalate through the IBM-vendor relationship manager
