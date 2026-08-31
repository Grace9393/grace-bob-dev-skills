# ServiceNow — Platform Reference

## Resolver Scope

ITSM modules (Incident, Problem, Change, Request), Service Catalogue, CMDB, Service Portal, Workflow/Flow Designer, Performance Analytics, Integration Hub, scripting (Business Rules, Client Scripts, Script Includes, Scheduled Jobs), ATF, Update Sets, Scoped Applications.

## Triage Signals

| Signal | Likely Category | Initial Action |
|--------|----------------|----------------|
| "Workflow stuck", "Flow not triggering" | Bug / Config | Check Flow/Workflow context, conditions, activity logs |
| "Portal page error" | Bug / UI | Check browser console, Service Portal widget logs, instance logs |
| "CMDB data incorrect" | Data / Config | Check Discovery schedule, reconciliation rules, import sets |
| "SLA not calculating" | Config | Check SLA Definition, conditions, schedule, timezone |
| "Update Set conflict" | Change / Deployment | Review Update Set preview log, resolve conflicts manually |
| "Catalogue item not visible" | Access / Config | Check user criteria, catalogue ACLs, category visibility |
| "Integration failure" | Integration | Check Integration Hub logs, MID Server status, credentials |
| "Performance slow" | Performance | Check slow queries, semaphore waits, node health |
| "Scheduled job not running" | Config / Bug | Check Scheduled Script Execution, node assignment, errors |

## Investigation Checklist

1. Identify the ServiceNow instance (Production, Sub-production, PDI)
2. Check System Diagnostics (stats.do) for node health and performance
3. Review System Logs for errors around the time of the issue
4. Check Update History for recent deployments
5. Review Background Scripts and Scheduled Jobs for recent changes
6. Check HI Service Portal for platform-wide incidents or maintenance
7. Verify instance version and latest patches

## Common Resolutions

**Workflow/Flow issues:** Check conditions, verify trigger, review activity log for errors, check ACLs on tables involved.
**Portal issues:** Clear browser cache, check widget script errors, verify data source accessibility.
**CMDB issues:** Re-run Discovery, check reconciliation rules, validate import set mappings.
**SLA issues:** Verify SLA Definition conditions match ticket, check business schedule, verify timezone alignment.
**Performance issues:** Identify slow-running Business Rules, optimise GlideRecord queries, check table indexing.

## Vendor Escalation (ServiceNow Support)

Portal: HI Service Portal (hi.service-now.com)
Required information: Instance URL, instance version, System Diagnostics output (stats.do), reproduction steps, screenshots, system logs.

Severity mapping:
| ServiceNow | IBM |
|------------|-----|
| Sev 1 (Production down) | P1 |
| Sev 2 (Significant impact) | P2 |
| Sev 3 (Limited impact) | P3 |
| Sev 4 (Minimal impact) | P4 |
