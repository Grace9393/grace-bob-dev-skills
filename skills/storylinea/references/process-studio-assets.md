# Process Studio Assets (02_process_studio/NN_{process_slug}/)

Two files **per process**, in a numbered subfolder per process
(`01_accounts_payable/`, `02_invoice_validation/`, …; slug = lowercase,
non-alphanumerics → `_`).

Resolve four roles per process before writing (keep identical across SOP,
baseline, training materials, and agents):
- **role0** — intake/clerk (e.g. Accounts Payable Clerk)
- **role1** — reviewer/specialist (e.g. AP Analyst)
- **role2** — approver (e.g. AP Manager)
- **role3** — senior/escalation (e.g. Finance Controller)

## process_sop.md — the document uploaded into Process Studio

```
# Standard Operating Procedure — {Process}
**Document type:** Standard Operating Procedure (SOP)
**Organisation:** {Company}
**Process:** {processes}
**Owner:** {role0's function}
**Approved by:** {role2} / Head of Process Excellence
**Effective date:** 01 January 2024
**Review date:** 01 January 2025
**Version:** 3.0
**Classification:** Internal
```

1. `## Purpose` — mandatory end-to-end SOP statement.
2. `## Scope` — applies-to bullets (all records of the process's primary
   object; the 4 roles; top 3 systems; all business units) + Exclusions
   sentence (third parties, sub-threshold items, external providers).
3. `## Roles and Systems` — `Role | Responsibility` table (4 rows) and
   `System | Purpose` table (up to 5 systems; vendor selections first).
4. `## Process Overview` — "begins when {domain trigger} and ends when
   {domain end state}", then 5 bolded phases each with a domain-specific
   paragraph: Initiation, Processing, Validation and Control, Approval
   (references the domain's authority terminology, e.g. Delegation of
   Authority), Completion.
5. `## Detailed Procedures` — 5 steps, each with **Owner:** and **System:**
   sub-lines and a numbered activity list:
   - Step 1 — Receive and Register (role0; Trigger line; Control point:
     verify sender authority)
   - Step 2 — Initial Validation (role0; cross-reference top 3 data objects;
     one business rule using domain terminology; **SLA:** 1 business day)
   - Step 3 — {domain review-step label: Review and Matching / Screening and
     Evaluation / Triage and Classification / Review and Assessment…}
     (role1; primary + secondary system; 4 activities; Control point:
     segregation of duties)
   - Step 4 — Approval (role2; 5 activities; decision recorded in the primary
     system; authority-limits line)
   - Step 5 — Processing and Completion (role0; 5 activities; **Audit
     requirement** line)
6. `## Controls` — `Control ID | Control Description | Frequency | Owner |
   Evidence` table, 5 rows with IDs `{FIRST-3-LETTERS}-CTL-001..005`. When two
   processes in the package share those first three letters (Claims intake and
   Claims triage both give `CLA`), append the process index — `CLA1-CTL-001`,
   `CLA2-CTL-001` — so the package's controls register has no duplicate IDs:
   completeness check (Per item / role0 / System log), segregation of duties
   (Per item / Process manager / Access control log), domain-specific control
   (Per item / role1 / domain evidence), approval within authority
   (Per item / role2 / Approval log), audit trail review (Monthly / Internal
   audit / Audit report).
7. `## Exceptions` — `Exception Type | Cause | Action Required | Owner | SLA`
   table, 5 rows: Validation failure (role0, 2 days); domain-specific
   exception (role1, manual investigation, 5 days); Approval delay (Process
   manager, escalate to delegate, 3 days); System error (IT Service Desk,
   log & retry, 1 day); Duplicate submission (role0, reject, 1 day).
8. `## Key Performance Indicators` — `KPI | Target | Measurement` table,
   4 domain KPIs, measured in the primary system. Phrase targets by direction:
   "At or above defined target" for higher-is-better KPIs, **"At or below
   defined target"** for lower-is-better ones (cycle time, exception rate,
   leakage, reassignment rate, reserve variance). Never label a
   lower-is-better KPI "at or above target" — it inverts the meaning.
9. `## Escalation` — `Level | Trigger | Escalation To | Action` table, 3 rows:
   L1 >2 days → role1; L2 >5 days → role2 + root cause; L3 systemic issue or
   compliance breach → role3 / Compliance Officer.
- Appendices: A — Glossary (6 domain terms); B — Related Documents (authority
  policy, vendor management, information security, first compliance
  framework); C — System Access Requirements.

## input_baseline.md — feeds the Process Studio business case

```
# Input Baseline — {Process}
**Organisation:** … **Process:** … **Industry:** … **Region:** … (if set)
**Complexity:** … **Primary system:** {system}
```

- Blockquote **"How to use this document"** — review and replace values with
  real data, then feed into Process Studio to generate the Business Case and
  ROI model; figures are calibrated to industry, region, and complexity.
- `## Baseline Metrics` — `# | Metric | Current Value | Notes` table, exactly
  **10 rows**: (1) monthly volume, (2) average handling time, (3) FTE count —
  note lists the 4 roles by function, value formatted as a split like
  `5 FTEs (3 processors + 2 reviewers)`, (4) exception rate %, (5) exception
  handling time, (6) secondary volume — note "System of record: {sys0}",
  (7) tertiary volume — note "Secondary system: {sys1}" (omit if same),
  (8) approval delay — note names role2 with role3 as delegate, (9) loaded
  labour rate, (10) incident count last 12 months — note "Detail below".
- `## Incident Detail (Row 10)` — 2–6 fictional incident bullets (count by
  complexity; include a control/SOX/audit finding only when complexity is not
  simple).
- `## Revenue and Cost Scope` — `Item | Value` table: annual revenue in scope,
  loaded labour rate, primary system, secondary system, top 3 compliance
  frameworks.
- `## How to Interpret These Metrics` — three subsections:
  - **Calculating the Manual Labour Cost Baseline** — fenced formula
    `Monthly volume × Average handling time (minutes) ÷ 60 × FTE hourly rate × 12`
    plus a worked example echoing the table's values.
  - **Calculating the Exception Cost Baseline** — fenced formula
    `Monthly volume × Exception rate % × Exception handling time (minutes) ÷ 60 × FTE hourly rate × 12`.
  - **Metrics to Confirm with Operations Team** — 6-item checklist.
- Footer: `*Generated by storylinEA · {Process} · {Industry} · {Region} · {Complexity}*`

### Calibration rules (make numbers internally consistent)

- **Complexity multipliers:** volumes ×0.4 / ×1.0 / ×2.5 and FTEs ×0.5 / ×1.0
  / ×2.0 for simple / moderate / complex; handling times, exception rates, and
  approval delays step up with complexity.
- **Region → currency & labour rate:** Western/Eastern Europe → EUR (≈€35/hr
  ~€58k FTE and ≈€18/hr ~€30k respectively); North America $45/~$75k; Latin
  America $15/~$25k; Middle East and Africa $22/~$37k; Asia Pacific $20/~$33k;
  Global/default $40/~$66k.
- **Revenue in scope:** simple ≈ 500M, moderate ≈ 2.5B, complex ≈ 10B+ (in the
  region's currency).
- **Derive the FTE count — never guess it.** One FTE supplies ~140 productive
  hours per month (1,680/year after leave, training and admin). So:

  ```
  monthly hours = volume × handling ÷ 60  +  volume × exception rate × exception handling ÷ 60
  FTE count     = monthly hours ÷ 140      (round to a whole number)
  ```
  Then split it in the displayed form, e.g. `48 FTEs (32 processors + 16 reviewers)`
  at roughly a 2:1 processor-to-reviewer ratio. A package whose FTE count is
  wildly below this is the single most common realism failure — a reviewer who
  divides the volume by the headcount will spot it immediately.
- **Round consistently and say so.** Round monthly hours to whole hours and
  annual totals to the nearest €100/$100, and state that convention where the
  worked example appears, so the figures in the prose reproduce the table
  exactly rather than drifting by a few euros.
- **Row 7 vs the 10-row rule:** if the secondary system equals the primary,
  replace row 7 with another meaningful volume metric rather than dropping it —
  the table is always 10 rows.
- Sanity-check before finishing: recompute both worked examples from the table
  rows, and confirm the FTE count matches the formula above.
