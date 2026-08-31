# storylinEA Package Contract

The generation config, folder layout, naming rules, and validation gates every
package must satisfy. Derived from the storylinEA app (github.ibm.com/zach-gilbert/storylinea).

## Generation inputs

Collect these before generating (ask only for what's missing; sensible defaults in parens):

| Input | Values | Notes |
|---|---|---|
| Company name | free text | If absent, invent a fictional one that fits the industry |
| Industry | Banking, Insurance, Retail, Consumer Packaged Goods, Manufacturing, Healthcare, Life Sciences, Energy and Utilities, Telecommunications, Public Sector, Federal, Travel and Transportation, Financial Services, Shared Services, Technology, Custom Industry | Custom Industry needs a one-line description |
| Processes | 1+ names from the bucket taxonomy below (or user-supplied) | One `02_process_studio/` subfolder per process |
| Complexity | simple \| moderate \| complex (moderate) | Alters content depth, not section skeletons |
| Region | North America, Latin America, Western Europe, Eastern Europe, Middle East and Africa, Asia Pacific, Global (Global) | Adds a "Regional focus" line + regional flavor |
| Persona focus | optional free text | Tilts narrative toward that role's concerns |
| Outputs | fullStory, contextStudio, processStudio, agenticAppStudio, productWorkbench (all on) | Toggle folders on/off |
| Special notes / uploaded docs / client profile | optional | Injected into story (see asset-templates) |
| Vendor selections | optional, per bucket (e.g. finance → SAP S/4HANA) | Vendor systems + vendor-native entity names take precedence over generic ones throughout |

## Process bucket taxonomy

- **finance:** Accounts payable, Invoice validation, Three-way match, Payment run execution, Period-end close, Budget request and approval, Forecasting and variance analysis, Vendor statement reconciliation, Journal entry and GL posting, Intercompany reconciliation
- **procurement:** Vendor onboarding, Procurement request to purchase order, Contract review, Vendor query management, Spend analysis and reporting, Supplier performance management, Catalogue management
- **hr:** Employee onboarding, Offboarding and exit management, Leave and absence management, Performance review cycle, Payroll processing, Benefits administration, Learning and development enrolment, Grievance and disciplinary process
- **recruitment:** Job requisition and approval, Candidate sourcing and screening, Interview scheduling and feedback, Offer management, Background and reference checking, New hire pre-boarding
- **operations:** Exception handling, Case management, Field service dispatch, Work order management, Inventory replenishment, Service request fulfilment, Incident and problem management, SLA monitoring and escalation
- **sales:** Customer onboarding, Order to cash, Quote to order, Customer complaint handling, Returns and refund processing, Account renewal management, Customer credit review
- **compliance:** Compliance review, Audit preparation and evidence gathering, Risk assessment and register management, Policy review and approval, Regulatory reporting, Data subject request handling, Incident reporting and investigation, Controls testing
- **it:** IT service request fulfilment, Change management, Access provisioning and deprovisioning, Software licence management, Vendor and contract management, IT asset lifecycle, Security incident response
- **supply:** Demand planning and forecasting, Purchase to receipt, Goods in and quality inspection, Warehouse management, Outbound logistics and shipping, Returns management, Supplier risk assessment
- **claims:** Claims intake, Claims triage and assignment, Claims investigation and validation, Reserve setting, Settlement and payment, Subrogation and recovery, Fraud detection and referral

## Folder layout

Package root: `storylinEA_{company_slug}_{industry_slug}/` where slug = lowercase, spaces → `_`.

```
00_story/                 business_story.md, demo_walkthrough.md, asset_inventory.md
01_context_studio/        schema.jsonld, company_overview.md, operating_model.md,
                          brand_guidelines.md, training_materials.md
02_process_studio/
  01_{process_slug}/      process_sop.md, input_baseline.md     (one per process, 01_/02_/… order)
03_agentic_app_studio/    agent_instructions_intake.md, agent_instructions_review.md,
                          sample_user_prompts.md
04_product_workbench/     product_vision.md
```

Folders appear only when their output toggle is on; `asset_inventory.md` is always generated.
File names are fixed lower_snake_case; only the schema is `.jsonld`.

## Validation gates (run before delivering)

1. **Required files per generated folder:** `00_story/business_story.md`,
   `01_context_studio/company_overview.md`, at least one
   `02_process_studio/*/process_sop.md`, `03_agentic_app_studio/agent_instructions_intake.md`,
   `04_product_workbench/product_vision.md`.
2. **No secrets:** no API keys or `ICA_2_0_API_KEY=...` values anywhere in any asset.
3. **Fictional data only:** every name, email, vendor/customer, transaction ID is invented;
   `asset_inventory.md` carries the verbatim data-privacy disclaimer.
4. **No diagnostic contamination in upload assets.** The **upload assets** are exactly:
   the four `01_context_studio/` source documents, `schema.jsonld`, every
   `process_sop.md`, and the two agent instruction files. These are pasted or uploaded
   straight into platform tools, so they must read as genuine internal company
   documents: no validation/repair language ("semantic score", "failed rules",
   "placeholder detection", "repair history", "FAIL") and no demo or generation
   meta-commentary.
   Everything else is **facilitator-facing** (`00_story/*`, `input_baseline.md`,
   `sample_user_prompts.md`, `product_vision.md`) and *should* carry demo framing —
   the baseline's "How to use this document" blockquote and its
   `*Generated by storylinEA · …*` footer are required, not contamination.
5. **Semantic fit per process:** SOP and baseline use the process's own core terminology,
   a plausible trigger event, and systems of record that belong to that domain; no
   wrong-domain terms (e.g. no "candidate pipeline" language inside Accounts payable).
6. **No unreplaced placeholders:** scan for `{`, `[TBD]`, `TODO`, and stray `######`.
   The Context ID placeholder is deliberate and allowed in exactly two places: the
   setup block at the top of each agent instruction file, and the demo_walkthrough
   step that instructs the facilitator to replace it. Nowhere else.
7. **Cross-references resolve:** every file path mentioned in the walkthrough and
   asset inventory exists in the package; step numbering matches the enabled outputs.
   **Citations too:** the agent instruction files cite SOP sections
   (`*[Source: process_sop.md, Section 6 — Approval and Authority]*`) — after all
   files exist, open the SOP and confirm each cited section number and title
   actually matches. Generators writing in parallel cannot know this; it needs a
   final pass over the finished package.
8. **Figures agree across files:** the volumes, FTE counts, exception rates and
   cycle times in `input_baseline.md` must not contradict the pain points in
   `business_story.md` or the current-state table in `operating_model.md`.

## Recommended test prompts (Context Studio)

Include/adapt these ten in walkthrough/sample prompts; parameterize on the first process:

1. "What are the main business challenges described in these documents?"
2. "What controls apply to the {process} process?"
3. "Which KPIs are currently below target and what actions are recommended?"
4. "Who is responsible for approving exceptions in {process}?"
5. "What compliance frameworks apply to {company}'s operations?"
6. "What is the escalation path for an exception that exceeds its SLA?"
7. "What are the root causes of the current process problems?"
8. "What evidence is required for a completed transaction?"
9. "What is the segregation of duties requirement for this process?"
10. "What does good look like at the end of the {process} improvement programme?"

## Style conventions

- British spelling throughout (organisation, modernise, analyse, catalogue, enrolment).
- Bold key-value metadata lines; `---` rules between H2 sections.
- Walkthrough steps use the rigid triad: action → **What to say:** (verbatim narrator
  script) → **Key point:** (takeaway), with optional `> **Note:**` callouts.
- Complexity/region/persona change content values, never section skeletons.
