# Story Assets (00_story/)

Three files. These are the *demo-facing* documents: the narrative, the
facilitator walkthrough, and the package inventory.

## business_story.md

```
# {Company} Business Story
## Company Snapshot
## Business Pressure
## Current-State Problem
## Why This Matters
## Selected Process Scope
## What the Documentation Reveals
## ICA / EA Demo Journey
## Target Outcome
## Demo Value
```

- **Company Snapshot** — company description (client-profile facts if supplied:
  employees, revenue, HQ, founded, key facts as bold key-value lines), then
  `**Industry:**`, `**Region:**`, `**Scale:** {size} — {employees} employees,
  {revenue} annual revenue`, `**Operating model:**`.
- **Business Pressure** — lead paragraph; `**External pressures:**` bullets
  (4–5, industry-specific); `**Internal pressures:**` bullets; closing line on
  compounding pace.
- **Current-State Problem** — "designed for a different scale" narrative;
  process-specific pain-point bullets; paragraph naming in-scope processes in
  bold; closing paragraph.
- **Why This Matters** — 5-row `Impact Area | Current State` table: Process
  efficiency, Financial exposure, Compliance and audit, Employee experience,
  Customer and partner trust; closing business-case line.
- **Selected Process Scope** — bold process list; if multiple processes, a
  cross-process-dependency paragraph, else a single-process "entry point"
  paragraph; `Complexity level: **{complexity}**`; `Regional focus: **{region}**`
  (only when region set); facilitator-notes block if special notes/docs supplied
  (`## Facilitator Notes and Client Context` with **Narrative context:** and
  **Reference documents supplied (N):** listing doc names).
- **What the Documentation Reveals** — numbered 1–5: Operating model gaps,
  Control weaknesses, KPI underperformance, Role/responsibility ambiguity,
  Process improvement opportunity — each pointing to the source doc where
  learners will find it.
- **ICA / EA Demo Journey** — the canonical 13-step `Step | Platform Area |
  Activity` table (see below).
- **Target Outcome** — 5 bullets: Process visibility, Intelligent automation,
  Grounded knowledge, Product direction, Audit-ready operations.
- **Demo Value** — two closing paragraphs naming the company and industry.

### The canonical 13-step demo journey

| Step | Platform Area | Activity |
|---|---|---|
| 1 | Context Studio | Upload Schema — `01_context_studio/schema.jsonld` |
| 2 | Context Studio | Upload Context — the four source documents |
| 3 | Context Studio | Test Prompts — explore extracted context |
| 4 | Process Studio | Connect to Context Studio |
| 5 | Process Studio | Upload SOP — `process_sop.md` |
| 6 | Process Studio | Analyse Process — steps, exceptions, controls |
| 7 | Process Studio | Build Business Case — `input_baseline.md` metrics → financial model |
| 8 | Product Workbench | Connect to Context Studio |
| 9 | Product Workbench | Create Project with Product Vision |
| 10 | Product Workbench | Test Application against process pain points |
| 11 | Agentic App Studio | Connect to Context Studio |
| 12 | Agentic App Studio | Create Two Agents (intake + review) |
| 13 | Agentic App Studio | Test Prompts — validate both agents |

## demo_walkthrough.md

```
# Demo Walkthrough — {Company}
## Purpose
## Pre-Demo Setup
## Step N — … (with timing in the heading)
## Close the Loop (5 minutes)
## Total Demo Time
```

- **Pre-Demo Setup** — 5-item checklist: environment provisioned; Context
  Studio files ready; business story reviewed; facilitator guide reviewed;
  ICA 2.0 API connection confirmed.
- **Steps are dynamically numbered** based on enabled outputs. Always: Read the
  Business Story (5 min) → Upload Schema (5) → Upload Source Documents (10) →
  Test Prompts (10). Then, per enabled output: Process Studio connect (5) +
  upload, analyse and build the business case (10); Product Workbench connect
  (5) + create project and test the application against the pain points (10);
  Agentic App Studio connect (5) + create two agents (15) + test prompts (10).
  Renumber consecutively; never leave gaps.
- **Cover all 13 journey activities.** The walkthrough has fewer steps than the
  13-step journey table, so the folded-in activities must still appear in the
  step body: Process Studio's *Build Business Case* from `input_baseline.md`,
  and Product Workbench's *Test Application against process pain points*.
- **Every step uses the triad:** action instruction → `**What to say:**`
  verbatim narrator script → `**Key point:**` takeaway; optional `> **Note:**`.
- Step 1's script is composed from the data: "{Company} is a {size} {sector}
  organisation. Their core challenge is: {first pain point}…"
- Schema step key point: **"Schema before content."** Source-doc step: upload
  the four docs as one batch; never upload schema.jsonld here; SOPs go to
  Process Studio, not Context Studio.
- Test-prompt steps embed 3 verbatim prompts (parameterize on the first process).
- Agent step: both instruction files carry a Context ID setup block whose
  `######` must be replaced with the real Context Studio Context ID; the two
  agents are connected in one workflow with an explicit handoff.
- **Close the Loop** — verbatim recap script: problem → documentation →
  process → product → agent.
- **Total Demo Time** — `Section | Duration` table with one row per enabled
  section and a total that is the **sum of the step durations you actually
  wrote**. The step headings are the single source of truth — add them up
  rather than applying a stored formula. With all outputs enabled the total is
  95 minutes (30 story + Context Studio, 15 Process Studio, 15 Product
  Workbench, 30 Agentic App Studio, 5 close).

## asset_inventory.md

```
# Asset Inventory — storylinEA Package
**Company:** … **Industry:** … **Processes:** … **Complexity:** …
**Generated by:** storylinEA
**Package name:** `storylinEA_{company_slug}_{industry_slug}.zip`

## File Inventory
| Folder | File | Purpose |          ← one row per file actually generated, in folder order
## Total File Count
**{N} files**
## Data Privacy Note
```

The Data Privacy Note is fixed: all names, emails, vendor and customer names,
transaction IDs, and identifiers in this package are fictional and generated
for demonstration purposes only. List the inventory's own row last
("This file — complete package inventory"); the count includes it.
