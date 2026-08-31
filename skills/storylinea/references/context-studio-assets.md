# Context Studio Assets (01_context_studio/)

Five files. The four markdown docs are written as *authentic internal company
documents* (not demo material) — each carries a document-metadata block
(followed by a `---`), formal corporate tone, British spelling, `---` between
H2 sections, and only fictional names. The schema is covered in
`jsonld-schema.md`.

Resolve a process-context profile per process: participants (roles), typical
systems (vendor selections take precedence), compliance frameworks, and data
objects appropriate to that process's domain — keep them consistent across all
five files and the Process Studio assets.

**How to read the counts below.** Numbers like "5 departments" or "4 compliance
frameworks" are *display caps for that section*, not the size of your
vocabulary. When your list is longer, show the first N in the specified form
and name the remainder in a closing sentence, so every term stays retrievable
in Context Studio. Truncation is deliberate layering — `operating_model.md`
shows the top 4 frameworks, `brand_guidelines.md` lists them all. Where a count
exceeds what you have, use what you have; never pad with invented filler.

## company_overview.md

```
# {Company} — Company Overview
**Document type:** Company overview
**Prepared by:** Corporate Communications / Strategy
**Audience:** Internal — all employees and partners
**Version:** 2.1
```
- `## About {Company}` — 2–3 sentence description (use researched client profile
  if supplied, else invent one fitting industry+complexity); market/sector and
  region sentence; optional **Key company facts:** bullets.
- `## Operating Scale` — Metric|Value table: annual revenue, employee headcount,
  geographic footprint, industry sector, primary markets, headquarters, founded.
  Scale numbers follow complexity (simple ≈ regional mid-size … complex ≈ global enterprise).
- `## Core Business Lines` — 5 departments, each `**{Dept}:** Responsible for …`.
- `## Strategic Priorities` — numbered 3: Operational excellence,
  Technology-enabled transformation, Compliance and risk management; closing
  sentence ties them to the in-scope process(es) in bold.
- `## Organisational Model` — org-model bullets referencing size, departments, region.
- `## Key Contacts (Fictional)` — Role|Name|Area table, ~5 invented people
  (COO, Finance Director, Head of Process Excellence, CCO, Head of Technology),
  plus fictional-names disclaimer.
- `## Document History` — 3–4 row version table.

## operating_model.md

```
# {Company} — Operating Model
**Document type:** Operating model reference
**Owner:** Head of Process Excellence
**Audience:** Internal — management and above
**Version:** 1.4
> **Note:** The process participants, systems, and KPIs below are specific to the **{processes}** process.
```
- `## Operating Model Overview` — the industry operating model in one paragraph.
- `## Process Scope: {processes}` — one heading with the processes comma-joined,
  then a numbered entry per process naming its top 3 participants and top 2 systems.
- `## Key Systems and Platforms` — System|Purpose|Owner table over all typical systems.
- `## Process Participants and Accountability` — Role|Function|Process involvement table.
- `## Governance Model` — 5 bullets (global process owners, local process managers,
  shared services leads, finance & compliance review, internal audit).
- `## Control Framework Summary` — 4 compliance frameworks, each one bullet.
- `## Current-State Assessment` — Process Area|Status|Primary Issue table; at
  minimum one row per process, all "Requires improvement", citing manual
  touchpoints / exception volume / cycle time above target. Splitting a process
  into sub-area rows is encouraged when it lets you land the baseline figures
  (this section seeds the demo's pain-point narrative, and Process Studio's
  baseline must not contradict it).
- `## Technology Roadmap Context` — 4 bullets, first names the primary system.

## brand_guidelines.md

```
# Brand Guidelines — {Company}
**Document type:** Brand and communications reference
**Owner:** Corporate Communications
**Audience:** Internal — all employees and platform administrators
**Version:** 1.0
**Data source:** {AI-researched brand data | Industry convention defaults}
```
- `## Brand Identity` — sector sentence + description + `**Brand personality:**`
  4 adjectives (use researched brand data when supplied; else pick an
  industry-appropriate set).
- `## Colour Palette` — source note; `Hex / Value | Role` table of 5 colours
  (`` `#HEX` `` | role, e.g. Deep Navy (primary)); Usage Rules bullets ending
  with "Do not introduce colours outside this palette."
- `## Typography` — Typeface|Role table (3 rows: primary, secondary, monospace
  for codes/IDs) + rules (min 11pt/14px, line spacing 1.4–1.6×).
- `## Terminology Standards` — Preferred Term|Avoid|Context table: ~6 domain
  data-object terms + 2 key roles + primary system ("Generic equivalents" in Avoid).
- `## Voice and Tone` — 5 principles (Direct, Professional, Precise, Grounded,
  Brand-aligned) + **Always avoid** bullets (hedging, unsourced claims,
  informality, competitor names, legal/financial/medical advice).
- `## Document and Content Standards` — Headings (sentence case), Lists, Tables
  ("—" for missing values), Dates and Numbers (DD Month YYYY / ISO 8601,
  currency with code, % to one decimal).
- `## Regulatory and Compliance Context` — all compliance frameworks as bullets
  + 3 "must" rules.
- `## Confidentiality Notice` — internal-use / fictional-data notice.

This file exists so Context Studio can answer brand/voice questions and so the
agents inherit terminology standards — keep its terminology consistent with the
schema entity names.

## training_materials.md

```
# Training Materials — {Company}
**Document type:** Training reference
**Process scope:** {processes}
**Owner:** Head of Process Excellence / HR
**Audience:** All process participants
**Version:** 1.0
```
- `## Purpose` — one paragraph.
- One `## {Process}` section **per process**, each containing:
  - `### Process Overview for Participants` — 4 roles, each with 4 bullets
    (end-to-end flow, exception routing, controls/compliance, system training).
  - `### Mandatory Training Requirements` — Role|Training Module|Frequency|Delivery
    Method table (per-role annual modules + all-roles compliance & data security
    + approver escalation training).
  - `### System Training` — primary system prerequisite, 4 modules, 80% pass assessment.
  - `### Onboarding Checklist` — 6 checkboxes incl. 5-day shadowing and approver sign-off.
  - `### Competency Framework` — Competency|Expected Level|Assessment Method, 5 rows.
  - `### Common Process Questions` — 3 Q&A (which systems, who approves
    exceptions, who resolves standard issues).

Length scales with process count — one full section each.
