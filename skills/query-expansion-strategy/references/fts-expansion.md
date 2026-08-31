# FTS Query Expansion — Detail Reference

---

## Sub-question Decomposition

Target 5–10 sub-questions per seed query. Each sub-question must be independently answerable and must map to at least one distinct token cluster in the index.

Decomposition categories (generate at least one per category where the seed permits):

| Category | Prompt Pattern | Example (seed: "how to prioritise leads") |
|---|---|---|
| Definition | What is [core concept]? | What is lead prioritisation? |
| Process | How do you [action]? | How do you rank sales prospects? |
| Rationale | Why does [action] matter? | Why is lead scoring important in B2B? |
| Comparison | How does [X] differ from [Y]? | How does lead scoring differ from lead grading? |
| Tooling | What tools support [action]? | What tools automate lead scoring? |
| Metrics | How is [outcome] measured? | What metrics indicate lead quality? |
| Mistakes | What errors occur when [action]ing? | What mistakes happen in lead prioritisation? |
| Trends | How is [topic] changing? | How is AI changing lead scoring? |
| Personas | How does [role] approach [topic]? | How do SDRs prioritise inbound leads? |
| Use-case | When should [action] be applied? | When should a startup implement lead scoring? |

---

## Synonym & Stemming Expansion

For each sub-question, generate 2–4 synonym variants. Expansion must account for FTS tokenisation:

- FTS5 default tokeniser (`unicode61`) splits on whitespace and punctuation, lowercases, and does **not** stem. Generated variants must therefore be lexically distinct tokens, not stemming assumptions.
- If the index was built with a stemming tokeniser (e.g. Porter via `tokenize = 'porter unicode61'`), stemming variants (score/scoring/scored) can be collapsed to the root form.

Expansion layers:

1. **Lexical synonyms** — Direct word substitutions. `prioritise` → `rank`, `order`, `sort`, `sequence`.
2. **Phrasal synonyms** — Equivalent multi-word expressions. `lead scoring` → `prospect evaluation`, `lead ranking`, `sales lead qualification`.
3. **Hypernym/hyponym expansion** — Broaden or narrow scope. `lead scoring` (hyponym of `sales pipeline management`); `MQL scoring` (hypernym narrows to a specific subtype).
4. **Colloquial / domain-specific variants** — Informal or industry-specific phrasing that users actually type. `lead scoring` → `how good is this lead`, `is this lead worth pursuing`.

---

## Entity Relationship Mapping

Build an entity graph around the seed topic. Each node must map to at least one token present in the target index. Structure:

```
Primary Topic: [Seed concept]
├── Related Concepts: [Closely linked abstractions]
├── Tools / Platforms: [Named software, APIs, vendors]
├── Metrics / KPIs: [Quantifiable outcomes]
├── Personas / Roles: [Who performs or is affected by this]
├── Use Cases / Verticals: [Industry or scenario framings]
└── Counter-concepts: [Alternatives, competitors, contrasts]
```

Example:

```
Primary Topic: Lead Scoring
├── Related Concepts: lead qualification, MQL, SQL, BANT, buyer intent
├── Tools: HubSpot, Salesforce, Marketo, Pardot
├── Metrics: conversion rate, lead velocity, cost per acquisition
├── Personas: SDR, AE, marketing ops, sales manager
├── Use Cases: B2B SaaS, enterprise, inbound marketing
└── Counter-concepts: manual lead review, account-based marketing
```

Include entity terms naturally distributed across generated query variants — do not front-load them into a single query.

---

## FTS Query Construction

Output is raw MATCH expression strings only — the value that goes inside `MATCH '...'`. Do not wrap in SELECT statements, reference table names, or include CLI flags. Execution is owned by the `sqlite-fts5-query` skill.

### Construction rules for expansion output

1. Default to implicit AND for multi-term queries unless OR fan-out is the explicit goal.
2. Use phrase matching (`"..."`) only when word order is semantically significant. `"lead scoring"` yes; `"how to score leads"` no — the latter will fail if the index contains `score leads` without `how to`.
3. Use prefix matching (`*`) for morphological variants when the index does **not** use a stemming tokeniser. When Porter is active, collapse to root form instead.
4. Strip all punctuation except `*` and `"` before submitting. FTS5 tokeniser will discard it anyway; leaving it in risks silent parse failures on edge cases.
5. Never generate a query that is exclusively composed of common stop words (`the`, `a`, `is`, `to`, `how`). Prepend or append at least one substantive token.
6. For synonym fan-out, combine variants into a single OR-joined expression rather than multiple separate expressions — one MATCH evaluation is faster than N.
7. Combine all constraints into a single expression using parentheses and boolean operators: `(a OR a2) AND (b OR b2)`. Do not produce multiple expressions where one will do.
8. Prefix operator (`*`) is invalid inside phrase quotes. `"digital service*"` will fail. Always place prefix terms outside quotes: `digital service*`.

### Output format

Each expanded query is a numbered MATCH expression string with a label.

```
Q1 [Core seed — synonym fan-out]:
("experience design" OR "UX design" OR "interaction design" OR "service design") AND ("public sector" OR government OR "public service") AND (UK OR Britain OR British OR "United Kingdom")

Q2 [Case study framing]:
("experience design" OR "UX design" OR "service design") AND ("case study" OR "case studies" OR "worked example" OR example*)
```

---

## Coverage Analysis Output

After generating the full expanded set, produce this analysis block. Use it as the deliverable to the user.

```
Target Query: [seed query]

Sub-Questions Generated: [N] / 10
  ☑ Definition
  ☑ Process
  ☐ Rationale          ← MISSING
  ☑ Comparison
  ☐ Tooling            ← MISSING
  ☑ Metrics
  ☑ Mistakes
  ☐ Trends             ← MISSING
  ☑ Personas
  ☑ Use-case

Synonym Expansion Coverage: [N] variants across [M] sub-questions

Entity Mapping:
  Concepts covered:  [list]
  Concepts missing:  [list]
  Tools covered:     [list]
  Tools missing:     [list]

FTS Queries Generated: [N]
  Phrase queries:    [N]
  OR fan-out queries:[N]
  Prefix queries:    [N]

Semantic Coverage Score: [X]%
  (Calculated as: sub-questions covered / 10 × 0.5 + entity nodes covered / total entity nodes × 0.5)

Gaps & Recommendations:
  1. [Specific missing sub-question — add query targeting it]
  2. [Missing entity cluster — distribute across existing variants]
  3. [Tokeniser risk — flag any query that may fail under default tokenisation]
```

Terminate with the query set and coverage block. No additional commentary unless a gap is a tokeniser-level failure risk.
