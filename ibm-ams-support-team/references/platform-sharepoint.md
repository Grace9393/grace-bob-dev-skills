# SharePoint — Platform Reference

## Resolver Scope

SharePoint Online, site collections, document libraries, lists, permissions and sharing, Power Automate (cloud flows linked to SharePoint), Teams-connected sites, search, OneDrive for Business, migration issues.

## Triage Signals

| Signal | Likely Category | Initial Action |
|--------|----------------|----------------|
| "Cannot access site" | Access / Permissions | Check site permissions, group membership, conditional access policies |
| "Document won't open" | Bug / Config | Check file format, co-authoring locks, browser compatibility |
| "Search not returning results" | Config / Performance | Check search schema, crawl schedule, managed properties |
| "Flow failing on SharePoint trigger" | Integration / Bug | Check Power Automate run history, connection credentials, throttling |
| "Permission inheritance broken" | Access / Config | Check unique permissions, sharing settings, sensitivity labels |
| "Storage quota exceeded" | Capacity | Check site storage usage, versioning settings, recycle bin |
| "Teams files not syncing" | Integration | Check Teams-SharePoint site connection, sync client status |
| "Migration errors" | Data / Change | Check migration tool logs, file path length, special characters |
| "Custom column/view missing" | Config | Check list settings, content types, site columns |

## Investigation Checklist

1. Identify the SharePoint environment (Online tenant, site collection URL)
2. Check Microsoft 365 Service Health for platform-wide issues
3. Review SharePoint Admin Centre for tenant-level settings
4. Check site permissions and sharing settings
5. Review audit logs in Microsoft Purview Compliance Centre
6. Check Power Automate run history for flow-related issues
7. Verify conditional access policies in Entra ID (Azure AD)

## Common Resolutions

**Permission issues:** Grant access via SharePoint group, check sharing settings at site and tenant level, review conditional access.
**Document issues:** Check out/check in to release locks, clear browser cache, verify file size limits.
**Search issues:** Re-index site, check managed property mappings, verify content source and crawl schedule.
**Flow issues:** Refresh Power Automate connection, check for throttling (429 errors), review trigger conditions.
**Storage issues:** Enable versioning limits, empty recycle bin (both stages), archive old content.

## Vendor Escalation (Microsoft Support)

Portal: Microsoft 365 Admin Centre > Support > New Service Request
Required information: Tenant ID, site collection URL, affected user UPN, browser/OS, reproduction steps, screenshots, diagnostic logs (if requested by Microsoft).

Severity mapping:
| Microsoft | IBM |
|-----------|-----|
| Sev A (Critical, service down) | P1 |
| Sev B (Service degraded) | P2 |
| Sev C (Non-critical) | P3/P4 |
