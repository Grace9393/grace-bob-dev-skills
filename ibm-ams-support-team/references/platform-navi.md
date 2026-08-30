# NAVI — Platform Reference

## Resolver Scope

IBM internal navigation and tooling platform. Access provisioning, portal navigation, custom integrations with IBM back-office systems, UI/UX issues, SSO and identity federation with IBM w3id.

## Triage Signals

| Signal | Likely Category | Initial Action |
|--------|----------------|----------------|
| "Cannot access NAVI" | Access / Authentication | Check w3id status, browser compatibility, VPN/network |
| "Page not loading" | Bug / UI | Check browser console, NAVI status page, clear cache |
| "Data not displaying" | Integration / Data | Check upstream data source connectivity, API health |
| "New user needs access" | Service Request | Follow standard access provisioning process |
| "Role/permission change needed" | Service Request | Verify approval, follow role assignment procedure |
| "Custom integration broken" | Integration | Check API endpoints, authentication tokens, data contracts |
| "Slow performance" | Performance | Check NAVI platform health, network latency, browser resources |

## Investigation Checklist

1. Identify the specific NAVI module or page affected
2. Check NAVI platform status and maintenance schedule
3. Verify the user's w3id authentication and role assignments
4. Check browser compatibility (supported browser and version)
5. Test VPN and network connectivity to IBM internal services
6. Review integration API health and response times
7. Check for recent platform deployments or configuration changes

## Common Resolutions

**Access issues:** Verify w3id credentials, clear browser cache and cookies, try incognito/private mode, check VPN connection.
**UI issues:** Clear browser cache, try supported browser, check for browser extension conflicts.
**Integration issues:** Verify API endpoint health, refresh authentication tokens, check data contract compatibility.
**Provisioning:** Follow standard onboarding process, verify manager approval, confirm role mapping.

## Vendor Escalation (IBM Internal)

Portal: IBM internal support channels
Required information: User's IBM serial number, w3id, NAVI module/page affected, browser/OS, screenshots, network trace if relevant.

Note: NAVI is IBM-internal — escalation follows IBM's internal support processes rather than external vendor channels. Engage the NAVI platform team directly through IBM's internal ticketing.
