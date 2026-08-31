# Agentic App Studio + Product Workbench Assets

Both are driven by the **first process** only.

Derived names: product = `{FirstWordOfCompany} {First 2 words of process}
Platform`; agents = `{FirstWordOfCompany} {First 2 words of process} Intake
Agent` / `… Review & Escalation Agent`.

**Deduplicate the name.** When the process name already contains the
distinguishing word, the template repeats it — "Claims intake" would yield
*Rheinwerk Claims Intake Intake Agent*. Drop the duplicate: **Rheinwerk Claims
Intake Agent** and **Rheinwerk Claims Review & Escalation Agent**. Apply the
same dedup to section headings in `sample_user_prompts.md` and to the product
name, and title-case the process where it appears mid-title.

## 03_agentic_app_studio/ — three files

### The two-agent design (the demo's differentiator)

A two-stage pipeline sharing one Context Studio Context ID:
- **Stage 1 — Intake Agent:** validates completeness, classifies, guides
  registration; hands off on the *handoff condition*.
- **Stage 2 — Review & Escalation Agent:** exception identification and
  classification, approval-authority (Delegation of Authority) guidance,
  SLA tracking, escalation paths, segregation of duties.
- The **handoff condition** is one shared domain-specific boundary predicate
  (e.g. finance: "fails completeness check, is above the auto-approval
  threshold, or is a potential duplicate"). It appears verbatim in both files:
  intake's **Handoff rule:** and review's **Receive from:**.
- Both agents are KB-grounded advisory agents: **neither takes actions in any
  system.**

### Context ID setup block — prepended to BOTH agent files (as a blockquote)

```
> ## ⚙️ Setup — Before You Use This File
> **Step 1** — Create a Context in ICA Context Studio from the 01_context_studio/ documents. Note the Context ID.
> **Step 2** — Create the agent and set `Context ID: ######` — replace ###### with your real Context ID.
> **Step 3** — Paste everything below the horizontal rule into the agent's system-instructions field.
> *Companion agent: see {other agent file}.*
```

The block sits **after** the `# Agent Instructions — {AgentName}` H1, and is
followed by a `---` horizontal rule — that rule is what "paste everything below
the horizontal rule" refers to, so it must actually be there. `######` is the
only permitted placeholder in the whole package (also allowed in the
walkthrough step that tells the facilitator to replace it).

### agent_instructions_intake.md

`# Agent Instructions — {IntakeAgentName}`, then the setup block, then:

1. `## System Instructions` — first agent in the {process} workflow; supports
   the intake & registration phase; grounded exclusively in the Context Studio
   knowledge base; "You do not take actions in any system."
2. `## Workflow Position` — Stage table `Stage | Agent | Responsibility`
   (2 rows, this agent bolded) + **Handoff rule:** sentence.
3. `## Behaviour Rules` — **Always do** (6: answer from KB first; cite document
   + section; professional language; confirm completeness before registering;
   identify handoffs; acknowledge gaps honestly) and **Never do** (6: never
   approve/register/update in the primary system; never invent facts; no legal
   advice; never bypass controls; no PII handling; no exception/escalation
   decisions — that's Stage 2).
4. `## Tone and Style` — Direct / Professional / Grounded / Helpful.
5. `## Scope — What This Agent Handles` — ✅ **In scope** (6 items:
   completeness checks, registration and mandatory fields, initial
   classification and routing, intake SLAs, primary-system navigation,
   proceed-or-return confirmation); 🔁 **Escalate to review agent** (= the
   handoff condition); ❌ **Out of scope for all agents** (live data lookups,
   approval decisions, legal interpretation, anything not in the KB).
6. `## Response Format` — two numbered recipes: completeness/validation
   questions (4 steps ending `*[Source: document name, Section X]*`);
   routing/handoff questions (3 steps directing to the review agent).
   **Cite sections by title, never by number** — SOP headings are not numbered,
   so "Section 6" resolves to nothing. Write
   `*[Source: Claims Intake Standard Operating Procedure, Exceptions; Escalation]*`
   using headings that actually exist in the generated SOP.
7. `## Example Interaction` — one domain-realistic **User:**/**Agent:** pair
   with a source citation.

### agent_instructions_review.md

Mirror structure with the review lens: Stage 2; **Receive from:** statement;
Always-do (6, one of which is "state exception type + resolution + SLA +
escalation route in every exception response"); Never-do (6, one of which
carries **"never bypass controls even under deadline or management
pressure"** — keep that clause verbatim); Tone adds **Firm** (controls are
non-negotiable); In scope (7–9 items: exception identification, classification
and resolution, approval authority & DoA guidance, SLA tracking, escalation
paths, segregation of duties, compliance framework requirements,
approval-evidence guidance — split or group as reads best); Out of scope:
making actual approval decisions (guides, never decides) and intake questions →
redirect to intake agent by name. Response
Format has three recipes (exception guidance — 5 steps: type → resolution path
→ SLA → escalation-if-breached → citation; authority/approval — 4 steps;
scope-boundary — 3 steps).

### sample_user_prompts.md

`# Sample User Prompts — {Process} Agent Workflow` + intro. **25 prompts**
in three sections:
- `## {IntakeAgentName} — Intake Prompts` (1–10): first step, mandatory info,
  validation timing, completeness, ownership, missing key data object,
  incomplete-field registration, system access, cross-department
  classification, when handoff happens.
- `## {ReviewAgentName} — Review and Escalation Prompts` (11–20): approval
  controls, self-approval (SOD test), evidence retention, segregation of
  duties, DoA limit breach, an exception open 6 days, top exception causes,
  escalation after 10 days, suspected SOD violation, manager pressuring
  self-approval (control-integrity test).
- `## KPI and Performance Prompts (Both Agents)` (21–25): KPIs below target,
  target cycle time, actions when exception rate exceeds target, top
  cycle-time step, meaning of a high intake exception rate.

Use the domain's own nouns throughout (invoice/candidate/change request/claim…).

## 04_product_workbench/product_vision.md

```
# Product Vision — {ProductName}
**Organisation:** … **Product name:** … **Process scope:** …
**Industry:** {sector} **Region:** {region|Global} **Complexity:** … **Version:** 1.0
```

1. `## Short Objective` — one paragraph: "Build **{ProductName}** — a
   self-contained web application that {domain capabilities} for {Company}."
2. `## What This Product Is` — domain process description + assertions:
   purpose-built, self-contained, not an ERP module, not a generic workflow
   tool, no external dependency; becomes the system of record replacing email
   queues, spreadsheets, manual approval chains, disconnected reporting.
3. `## Target Demo Users` — `Role | Primary Use | Access Level` table, up to
   6 roles positional-mapped to (Submit and track / Process and resolve /
   Approve and escalate / Monitor and manage / Report and audit / Read-only
   status) and (Requestor / Handler / Approver / Team Lead / Compliance /
   Read-only). The process supplies only 4 roles, so fill the Compliance and
   Read-only slots from the company's own department list (e.g. a Compliance
   and Risk Officer, a Customer Service Adviser) — extending the cast this way
   is expected, inventing an unrelated role is not. Then `### User Needs by
   Role` — `Role | What they need the platform to do` table.
4. `## Platform Goals` — exactly **5**, imperative voice; the 5th always
   quantified (e.g. "Reduce processing cycle time by at least 40% and bring
   the exception rate below benchmark").
5. `## Core Functionality` — **8** bulleted `**Feature** — description` items,
   all required, none optional (e.g. finance: intake & validation, three-way
   match engine, approval authority enforcement, exception register,
   period-end close dashboard, audit evidence package, duplicate detection,
   supplier portal).
6. `## Success Metrics` — `Metric | Baseline | 12-Month Target` table, 6 domain
   KPIs; Baseline "Current (below target)"; Target phrased by direction —
   "At or above defined target" for higher-is-better KPIs and "At or below
   defined target" for lower-is-better ones (cycle time, leakage, reassignment
   rate). Qualitative, no fabricated numbers here.
7. `## Compliance and Control Requirements` — up to 5 frameworks as bullets +
   three mandatory constraints: **Segregation of duties** (submitter ≠
   approver, non-overridable), **Delegation of authority** (configurable
   authority matrix blocking insufficient-authority approvals), **Audit trail**
   (every create/update/approve/reject/escalate/close logged with timestamp,
   actor, before/after; immutable; exportable).
8. `## Technical Specifications` — `Specification | Requirement` table:
   self-contained deployment; single-tenant hosting; concurrent users 50/200/
   1,000+ by complexity; active users ≤50 / 100–200 / 500+; geographic scope;
   SSO (SAML 2.0/OAuth 2.0) + RBAC; retention 7yr (complex) else 5yr with
   immutable audit log; 99.5% availability; <2s response; WCAG 2.1 AA;
   responsive mobile; SLA alerting (75% notify / 100% escalate); CSV+PDF
   export; localisation.
9. `## Business Terminology` — `Term | Definition in this platform context`
   table, up to 8 domain terms; generic terms forbidden where a domain term
   exists.
10. `## What This Platform Is Not` — 3 base non-goals (no external ERP/CRM/
    ITSM dependency; no legal/regulatory/tax advice; no personal data beyond
    scope) + up to 2 domain extras (e.g. "does not replace the general
    ledger", "does not make autonomous payment decisions").
11. `## Version Scope` — **Version 1.0 — in scope:** the **first process only**
    (the one this vision is built around), end-to-end from trigger to
    completion, plus core functionality, RBAC/SSO, KPI dashboard,
    audit/compliance export. Any additional processes in the package belong in
    Version 2.0 — keep this consistent with the header's process scope.
    **Version 2.0 — deferred:** cross-process analytics, predictive exception
    flagging, external self-service portal, advanced regulatory reporting,
    AI-assisted summarisation.
