# Salesforce Scope-Limiting Bounding Statements

## Domain-Specific Boundaries for Salesforce Projects

### 1. Salesforce Edition and License Boundaries

**Bounding Statements:**
- "Solution designed for Salesforce Enterprise Edition; Professional Edition requires re-architecture"
- "Assumes [number] Sales Cloud licenses, [number] Service Cloud licenses"
- "Platform licenses excluded; requires full user licenses"
- "Sandbox environments: 1 Full, 2 Partial; additional sandboxes client responsibility"
- "API call limits: solution operates within [percentage]% of org limits"

**Risk Mitigation:**
- Prevents edition-specific feature assumptions
- Clarifies license procurement responsibilities
- Establishes sandbox strategy upfront
- Protects against API limit violations

### 2. Salesforce Object and Field Limits

**Bounding Statements:**
- "Custom objects limited to [number]; standard objects used where possible"
- "Maximum [number] custom fields per object"
- "Formula fields limited to [number] per object due to performance"
- "Lookup relationships capped at [number] per object"
- "Master-detail relationships: maximum [number] per object"

**Risk Mitigation:**
- Prevents hitting Salesforce governor limits
- Manages data model complexity
- Protects against performance degradation
- Establishes clear data architecture boundaries

### 3. Automation and Code Boundaries

**Bounding Statements:**
- "Declarative automation preferred; Apex code only where necessary"
- "Maximum [number] workflow rules, [number] process builders, [number] flows"
- "Apex code coverage minimum 85%; test classes included"
- "Trigger framework: one trigger per object maximum"
- "Batch Apex jobs limited to [number]; scheduled jobs capped at [number]"

**Risk Mitigation:**
- Prevents automation sprawl and conflicts
- Establishes code quality standards
- Manages governor limit exposure
- Clarifies technical approach

### 4. Integration Scope (Salesforce-Specific)

**Bounding Statements:**
- "Integrations via REST API only; SOAP API excluded"
- "Real-time integrations limited to [number] systems"
- "Batch integrations: maximum [frequency] per day"
- "Middleware: client-provided (MuleSoft/Dell Boomi/etc.)"
- "Platform Events limited to [number] event types"

**Risk Mitigation:**
- Clarifies integration architecture
- Establishes middleware ownership
- Limits integration complexity
- Protects against integration failures

### 5. User Interface Customization Boundaries

**Bounding Statements:**
- "Lightning Experience only; Classic UI not supported"
- "Standard Lightning components used; custom LWC limited to [number]"
- "Page layouts: maximum [number] per object"
- "Record types: limited to [number] per object"
- "Mobile app: Salesforce Mobile App only; custom mobile app excluded"

**Risk Mitigation:**
- Prevents UI complexity explosion
- Clarifies mobile strategy
- Establishes component reuse approach
- Manages maintenance burden

### 6. Data Migration Boundaries (Salesforce)

**Bounding Statements:**
- "Data migration via Data Loader; ETL tools excluded"
- "Historical data: [timeframe] only; older data archived"
- "Data cleansing: deduplication and format standardization only"
- "Attachments/files: maximum [size] per record, [total size] overall"
- "Migration validation: [percentage]% sample verification"

**Risk Mitigation:**
- Manages migration complexity and duration
- Establishes data quality responsibilities
- Protects against storage limit violations
- Clarifies validation approach

### 7. Salesforce Security and Sharing

**Bounding Statements:**
- "Security model: [approach] (e.g., private with sharing rules)"
- "Profiles: maximum [number]; permission sets preferred"
- "Sharing rules: limited to [number] per object"
- "Field-level security: defined for [user types] only"
- "External sharing: excluded unless explicitly scoped"

**Risk Mitigation:**
- Prevents security model complexity
- Establishes access control approach
- Manages sharing rule performance impact
- Clarifies external user strategy

### 8. Salesforce Reporting and Analytics

**Bounding Statements:**
- "Standard reports and dashboards: [number] included"
- "Custom report types: maximum [number]"
- "Dashboard components: maximum [number] per dashboard"
- "Einstein Analytics/Tableau CRM: excluded from scope"
- "Report scheduling: maximum [number] scheduled reports"

**Risk Mitigation:**
- Prevents unlimited reporting requests
- Establishes analytics platform boundaries
- Manages report performance impact
- Clarifies advanced analytics exclusions

### 9. Salesforce CPQ/Revenue Cloud Boundaries

**Bounding Statements:**
- "CPQ product catalog: maximum [number] products"
- "Price rules: limited to [number] active rules"
- "Quote templates: [number] templates included"
- "Approval processes: maximum [number] approval steps"
- "Advanced approvals and contracted pricing excluded"

**Risk Mitigation:**
- Manages CPQ complexity
- Establishes pricing rule boundaries
- Clarifies approval workflow scope
- Protects against performance issues

### 10. Salesforce Communities/Experience Cloud

**Bounding Statements:**
- "Community template: [specific template] (e.g., Customer Service)"
- "Community users: maximum [number] members"
- "Custom branding: logo and colors only; full rebrand excluded"
- "Community pages: maximum [number] custom pages"
- "External integrations from community: excluded"

**Risk Mitigation:**
- Establishes community platform boundaries
- Manages user licensing costs
- Clarifies customization scope
- Protects against community complexity

---

## Salesforce-Specific Risk Scenarios

### Governor Limits Protection
**Scenario:** Client wants unlimited automation
**Bounded Response:** "Solution designed to operate within 70% of Salesforce governor limits (SOQL queries, DML statements, CPU time). Exceeding these thresholds requires architecture review and potential re-design."

### Edition Limitations
**Scenario:** Client on Professional Edition wants Enterprise features
**Bounded Response:** "Proposed solution requires Salesforce Enterprise Edition for: workflow rules, approval processes, API access. Professional Edition implementation requires alternative approach with reduced functionality."

### Customization vs. Configuration
**Scenario:** Client wants extensive custom development
**Bounded Response:** "Solution prioritizes declarative configuration (80%) over custom code (20%). Custom Apex/LWC development limited to: [specific use cases]. Additional custom development requires separate SOW."

---

## Salesforce Project Estimation Impact

Proper Salesforce scope bounding reduces estimates by:
- **Data Model Complexity:** 25-35% reduction (clear object/field limits)
- **Automation Scope:** 30-40% reduction (defined automation boundaries)
- **Integration Effort:** 20-30% reduction (specific integration approach)
- **Testing Effort:** 15-25% reduction (clear test coverage requirements)
- **Overall Salesforce Project:** 20-30% reduction in total estimate