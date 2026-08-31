# Salesforce – Platform Reference (Enhanced)

## Resolver Scope

CRM configuration, Apex/Flow debugging, Lightning Web Components, Experience Cloud, integrations (REST/SOAP/MuleSoft), security and permissions, data operations, Agentforce.

## Triage Signals

| Signal | Likely Category | Initial Action |
|--------|----------------|----------------|
| "Apex error", "System.Exception" | Bug / Defect | Check debug logs, governor limits |
| "Flow failed", "Unhandled fault" | Bug / Defect | Review Flow version history, fault paths |
| "Cannot see record", "Insufficient privileges" | Access / Permissions | Check profile, permission sets, sharing rules, OWD |
| "Login failed", "SSO error" | Access / Authentication | Check IdP config, SAML assertions, My Domain |
| "API limit exceeded" | Performance / Limits | Review API usage (Setup > System Overview) |
| "Report shows wrong data" | Data / Config | Check report filters, FLS, record types |
| "Slow page load" | Performance | Check LWC rendering, SOQL in loops, CPU time |
| "Integration sync failed" | Integration | Check Connected App, Named Credentials, API logs |
| "Deployment failed" | Change / Deployment | Validation errors, test coverage, metadata conflicts |
| "Batch job stuck" | Async Processing | Check Apex Jobs, queueable depth, batch scope size |
| "Email not delivered" | Platform Services | Check Deliverability, Email Relay, DKIM/SPF |
| "Trigger recursion" | Code Quality | Review static flags, trigger context vars, execution order |

## Investigation Checklist

### Environment Context
1. Identify org type (Production, Full Sandbox, Partial Copy, Developer, Scratch)
2. Record org ID (Setup > Company Information)
3. Note Salesforce release version (Winter/Spring/Summer)
4. Check trust.salesforce.com for platform-wide issues
5. Review org edition and licensed features (Enterprise/Unlimited/Professional)

### Change Control
6. Setup Audit Trail: filter by date range, user, action type
7. Deployment History: check last 7 days for apex/trigger/flow changes
8. Change Sets: review inbound/outbound for pending promotions
9. Package Upgrades: check Installed Packages for recent version changes
10. Metadata API Deployments: query DeployRequest records via Workbench

### Runtime Analysis
11. Debug Logs: set FINEST trace flags for USER_DEBUG, CALLOUT, VALIDATION_RULE, WORKFLOW
12. Event Monitoring: query LoginEventStream, ReportEventStream, LightningPageViewEventStream (if licensed)
13. Governor Limits: check System Overview for SOQL queries, DML rows, CPU time, heap size
14. Asynchronous Apex Jobs: filter by status (Queued, Processing, Failed), check abort reasons
15. Flow Interview Logs: enable debug for specific flow, check fault email configuration

### Data Integrity
16. Field History Tracking: check if enabled on object, review audit trail
17. Duplicate Management: check matching/duplicate rules execution
18. Validation Rules: review active rules, check LastModifiedDate
19. Workflow Rules/Process Builder: confirm active status, entry criteria
20. Record-Triggered Flows: check trigger order, before/after context

### Integration Layer
21. Named Credentials: check authentication status, certificate validity
22. Connected Apps: review OAuth callback URL, refresh token policy
23. Remote Site Settings: confirm HTTPS URLs whitelisted
24. API Usage Dashboard: analyse calls by user, app, endpoint
25. Outbound Messages: check delivery status, retry queue
26. Platform Events: monitor event bus delivery metrics

### Security & Access
27. Profiles: compare object/field permissions between working/non-working users
28. Permission Sets: check assigned users, expiration dates
29. Sharing Rules: review criteria-based/ownership-based, recalculation status
30. Organisation-Wide Defaults: confirm Account/Contact/Custom object settings
31. Role Hierarchy: verify user placement, grant access using hierarchies checkbox
32. Manual Sharing: query AccountShare, ContactShare for specific records
33. Field-Level Security: check hidden/read-only settings on problematic fields

### Performance Diagnostics
34. Lightning Web Component Metrics: use Chrome DevTools Performance tab, LWC Performance Analyzer
35. Aura Debug Mode: enable for Lightning pages, analyse component timing
36. SOQL Query Plan: use Query Plan tool in Developer Console for selective filters
37. View State Size: check for Visualforce pages (max 170KB standard, 135KB mobile)
38. Skew Detection: identify records with >10,000 child records causing lock contention
39. Parallel API Calls: check if multiple threads hitting same record causing UNABLE_TO_LOCK_ROW

## Common Resolutions

### Permission Issues
**Missing Permission Set assignment:** Setup > Users > Permission Set Assignments
**Sharing rule gap:** Setup > Sharing Settings > review criteria-based rules, rebuild if needed
**Field-Level Security:** Profile/Permission Set > Object Settings > edit field permissions
**Record Type visibility:** Profile > Record Type Settings > enable assignment and default
**Lightning Page visibility:** App Builder > Activation > set org/app/record type defaults

### Flow Failures
**Add fault connector:** Connect failed path to Screen or Email Alert for visibility
**Null-check with Decision:** Add "Is Null" decision before Get/Update/Delete elements
**Bulkify DML/SOQL:** Use "Get Records" once before loop, collect IDs in collection variable, single Update after loop
**Avoid triggers firing flows firing triggers:** Use $Setup.FlowSettings__c.DisableTriggers__c custom setting
**Transaction finalizers:** Implement Queueable with System.Finalizer for guaranteed cleanup

### Apex Issues
**Governor limit exceeded:** Move SOQL outside loops, use Collection methods (Map.get vs nested queries), implement batch/queueable for large data
**CPU timeout (>10s):** Reduce complex calculations, offload to @future/queueable, simplify trigger logic
**Heap size (>6MB sync, >12MB async):** Clear collection references, use transient keyword, stream large query results
**UNABLE_TO_LOCK_ROW:** Implement retry with exponential backoff, lock row order consistently, reduce transaction scope
**Mixed DML operation:** Separate setup/non-setup DML into @future method, use System.runAs for test context

### Integration Failures
**OAuth token expired:** Named Credential > Edit > re-authenticate or implement refresh token handling
**API version mismatch:** Update endpoint version in code (v59.0 → v61.0), check deprecated API features
**Certificate expiry:** Setup > Certificate and Key Management > upload new cert, update Connected App
**Timeout on callout:** Increase timeout in HTTP request (max 120s), implement circuit breaker pattern
**Callout from trigger:** Move to @future(callout=true) or Queueable with implements Database.AllowsCallouts
**Retry logic:** Implement 3 attempts with 2^n backoff, check Retry-After header, log to Platform Event

### Deployment Issues
**Insufficient test coverage:** Write unit tests for new Apex (min 75% org-wide, 1% per class), use System.runAs for profile testing
**Metadata conflicts:** Compare source/target with SFDX force:source:pull, resolve in VS Code merge tool
**Component dependencies:** Deploy in sequence: Custom Objects → Fields → Validation → Triggers → Flows → Profiles
**Deployment timeout:** Split into smaller change sets (<5,000 components), deploy during maintenance window
**Quick Deploy unavailable:** Full validation must succeed in last 4 days, zero test failures, no destructive changes

### Data Issues
**Duplicate records:** Enable Duplicate Management, create Matching Rule (fuzzy/exact), activate Duplicate Rule (Alert/Block)
**Mass update failures:** Use Data Loader batch size 200, enable "Insert Null Values", check field dependencies
**Record locked during update:** Query with FOR UPDATE, implement pessimistic locking, reduce parallel job count
**Incorrect formula results:** Check field-level security (hidden fields return null), circular references, cross-object field deletions
**Missing history tracking:** Enable Field History (max 20 fields/object), retention period 18 months (or 24 with Shield)

### Performance Degradation
**Slow list views:** Reduce columns, add filters on indexed fields (Name, OwnerId, CreatedDate, RecordTypeId, SystemModstamp), enable Performance Edition
**Report timeouts:** Add filters to reduce dataset, move complex formulas to scheduled refresh, consider CRM Analytics
**Lightning page slow load:** Reduce component count, implement conditional rendering, lazy-load related lists, optimise Apex controllers
**Visualforce view state:** Use transient keyword on variables, enable view state compression, cache static resources
**API throttling:** Respect rate limits (15,000/24hr standard), implement exponential backoff, use Bulk API 2.0 for large operations

### Asynchronous Processing
**Queueable chain limit:** Max 5 depth from single transaction, use Platform Events for decoupling
**Batch job failures:** Reduce scope size (200 → 50), implement Database.Stateful for state tracking, check start/execute/finish errors separately
**Scheduled Apex not running:** Max 100 scheduled jobs, check Time Zone offset, avoid 02:00-03:00 maintenance window
**Future method limit:** 50 per transaction, consider queueable for chaining, check mixed DML restrictions

## Vendor Escalation (Salesforce Support)

**Portal:** help.salesforce.com (login with Salesforce credentials)

**Before logging:**
- Replicate in sandbox if possible
- Collect debug logs (Setup > Debug Logs > New)
- Export Setup Audit Trail (filter last 7 days)
- Screenshot error messages with timestamp
- Document affected user IDs and record IDs

**Required information:**
- Org ID (Setup > Company Information > Salesforce.com Organization ID)
- User ID (user detail page URL or SOQL query)
- Debug log excerpts (attach .log files, highlight ERROR/EXCEPTION lines)
- Reproduction steps (numbered, include navigation path)
- Release version (Setup > Release Updates)
- Browser/device (if UI issue)
- Expected vs actual behaviour

**Severity mapping:**
| Salesforce | IBM | Response SLA | Description |
|------------|-----|--------------|-------------|
| Sev 1 (Production down) | P1 | 1 hour | Core functionality unavailable, business stopped |
| Sev 2 (Major feature broken) | P2 | 4 hours | Major feature degraded, workaround possible |
| Sev 3 (Minor issue) | P3 | 1 business day | Minor feature issue, limited user impact |
| Sev 4 (Question) | P4 | 2 business days | How-to question, feature request |

**Known Issue search:** issues.salesforce.com (check before escalating)
**Premier Success add-on:** Faster response, named support engineer, architectural guidance

## Agentforce-Specific Guidance

### Configuration Layers
1. **Agent Topic Configuration:** Setup > Agentforce > Topics > check classification accuracy, test utterance matching
2. **Action Mapping:** Verify flow/apex action linked correctly, check input/output variable mapping
3. **Guardrail Configuration:** Review blocked entities, PII detection sensitivity, content filtering rules
4. **Einstein Trust Layer:** Audit logs for toxicity scores, data masking applications, grounding accuracy
5. **Prompt Template Versioning:** Compare active vs previous versions, check variable substitution syntax
6. **Channel Deployment:** Confirm agent activated on Experience Cloud, Messaging, Einstein Bots

### Diagnostics
7. **Conversation Logs:** Setup > Agentforce > Analytics > filter by agent, date range, intent confidence
8. **Action Execution Trace:** Debug logs with category EINSTEIN_AGENT set to FINEST
9. **Grounding Source Check:** Verify knowledge article visibility, Data Cloud segment filters, CMS content permissions
10. **Fallback Behaviour:** Test unhandled topics, check default response configuration
11. **Handoff to Human:** Verify queue assignment, omnichannel routing configuration, presence status

### Performance & Quality
12. **Intent Classification Accuracy:** Target >85%, retrain with additional utterances if below threshold
13. **Response Latency:** Median <3s, check action execution time in logs, simplify complex flows
14. **Planner Success Rate:** Monitor action completion vs abandonment, add clarification prompts for ambiguous requests
15. **Grounding Relevance:** Check retrieved chunk similarity scores, adjust retrieval count (default 5), refine metadata filters

### Common Issues
**Agent not responding:** Check active status, deployment timestamp, Experience Cloud guest user permissions
**Incorrect action triggered:** Review topic training data, test with Topic Tester tool, add negative examples
**Grounding hallucination:** Enable Einstein Trust Layer citation mode, reduce generative response length, increase grounding threshold
**PII leaked in response:** Configure data masking rules, check custom action output sanitisation, review prompt templates for variable exposure
**Integration action timeout:** Increase callout timeout in flow, implement async pattern with callback, add user-facing progress indicator