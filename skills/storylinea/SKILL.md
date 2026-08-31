---
name: storylinea
description: >
  Generate a complete storylinEA-style demo package for IBM Consulting
  Advantage (ICA / EA): business story, demo walkthrough, Context Studio
  JSON-LD schema + source documents, per-process SOPs and baselines for
  Process Studio, two connected agent instruction files for Agentic App
  Studio, and a Product Workbench product vision. Use whenever the user asks
  for an ICA/EA demo package, enablement lab assets, a storylinEA package, a
  scripted ICA demo for a company/industry/process, or "demo assets for
  Context Studio / Process Studio / Agentic App Studio / Product Workbench".
metadata:
  source: github.ibm.com/zach-gilbert/storylinea (converted 2026-07-24)
  classification: IBM Internal — generated packages are fictional demo data
---

# storylinEA — ICA / EA Demo Package Generator

Generate the full folder of demo/enablement assets the storylinEA app
produces, directly as files — no app required. The package tells one coherent
story: a fictional (or researched) company with a struggling process, whose
documentation is uploaded to **Context Studio**, analysed in **Process
Studio**, turned into a product vision in **Product Workbench**, and operated
by **two connected agents** in **Agentic App Studio**.

## Workflow

1. **Collect inputs** (`references/package-contract.md` has the full table):
   company name (invent if absent), industry (16 options), 1+ processes (use
   the bucket taxonomy), complexity (simple/moderate/complex), region,
   optional persona focus / special notes / client research / vendor
   selections (vendor systems and entity names take precedence everywhere).
   Ask only for what's missing and can't be sensibly defaulted; a bare
   "generate a demo for a Taiwanese bank, accounts payable" is enough.

2. **Fix the shared vocabulary first** — before writing any file, decide and
   keep consistent across ALL assets: the 4 process roles (intake clerk,
   reviewer, approver, senior escalation), the systems list, 4–6 compliance
   frameworks, 6–8 domain data objects / terminology, 4–6 domain KPIs, and
   the schema entity names. Inconsistency between files is the #1 quality
   failure.

3. **Generate the package** into `storylinEA_{company_slug}_{industry_slug}/`
   following the folder layout in `references/package-contract.md`:
   - `00_story/` → `references/story-assets.md`
   - `01_context_studio/` → `references/context-studio-assets.md` and
     `references/jsonld-schema.md`
   - `02_process_studio/NN_{slug}/` per process → `references/process-studio-assets.md`
   - `03_agentic_app_studio/` + `04_product_workbench/` → `references/agentic-workbench-assets.md`
   - `00_story/asset_inventory.md` last, listing exactly what was generated.
   Honor output toggles if the user only wants some studios; renumber the
   walkthrough steps accordingly.

4. **Validate before delivering** — run the gate checklist in
   `references/package-contract.md`: required files present, no secrets, all
   data fictional, no diagnostic/validation language inside upload assets, no
   unreplaced placeholders (the `######` Context ID marker is allowed only in
   the two agent files' setup blocks and the walkthrough step that tells the
   facilitator to replace it), process terminology matches the process domain,
   walkthrough cross-references and step numbering resolve, baseline math in
   the worked examples is correct and the FTE count matches the capacity
   formula. Then do one **whole-package consistency pass** that no individual
   file can do alone: agent citations point at real SOP sections, and the
   baseline figures don't contradict the story or the operating model. Fix and
   re-check; don't ship a package that fails a gate.

5. **Package** — zip the folder as `storylinEA_{company_slug}_{industry_slug}.zip`
   when the user wants a downloadable, otherwise leave the folder.

## Non-negotiable rules

- **Fictional data only.** Every person, email, vendor, customer, amount, and
  ID is invented. Never include real personal data. If the user supplies real
  client research, use only public company-level facts.
- **No secrets.** Never write API keys (`ICA_2_0_API_KEY` etc.) into any
  asset. ICA connection details stay in the environment.
- **British spelling** and formal corporate tone in all company documents.
- **Schema before content:** the walkthrough must upload `schema.jsonld`
  first, then the four source docs; SOPs go to Process Studio, never Context
  Studio.
- **Agents advise, never act:** both agent instruction files state the agent
  takes no system actions and never bypasses controls, even under pressure.
- Complexity, region, persona change *content values* (scale numbers,
  currency, labour rates, incident counts, narrative emphasis) — never the
  section skeletons.

## References (read the ones you're generating)

- `references/package-contract.md` — inputs, bucket taxonomy, folder layout,
  validation gates, test prompts, style rules. **Always read this one.**
- `references/story-assets.md` — business story, demo walkthrough (dynamic
  step numbering, What-to-say/Key-point triad), asset inventory.
- `references/context-studio-assets.md` — the four source documents.
- `references/jsonld-schema.md` — schema.jsonld node types, sizing by
  complexity, ID conventions, vendor-native entity names.
- `references/process-studio-assets.md` — SOP + input baseline, roles,
  calibration math (complexity multipliers, region currency/labour rates).
- `references/agentic-workbench-assets.md` — two-agent design with handoff
  condition and Context ID block, 25 sample prompts, product vision.
