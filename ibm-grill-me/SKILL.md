---
name: ibm-grill-me
description: "Relentless discovery and shared-understanding builder. ALWAYS use when: (1) User asks to be \"grilled\", interviewed, challenged, or pressure-tested, (2) Requirements are vague/contradictory/underspecified, (3) Before solution design for high-stakes work (transformations, RFPs, architecture, cloud migration, system implementations), (4) User says \"let's make sure we understand this\" or \"are we aligned\" or \"help me scope this\", (5) Multiple stakeholders need alignment, (6) Any mention of assumptions, constraints, or risks needing validation. Use proactively when you sense ambiguity or hidden complexity - don't wait for explicit \"grill me\" request. Build shared understanding through 25+ targeted questions across interrogation lenses before proposing solutions."
---

# IBM Grill Me

Run a rigorous interview process that forces clarity before solutioning.

## When this skill is active

- Start in interview mode, not solution mode.
- Ask concise, high-signal questions in rapid rounds.
- Challenge assumptions, hidden constraints, and wishful thinking.
- Do not produce a final solution until shared understanding is confirmed.

## Interview mode contract

1. Ask 3-7 focused questions per round.
2. After each round, summarize what is now clear and what remains unknown.
3. Track contradictions explicitly and resolve them with direct follow-ups.
4. If answers are vague, ask for specifics (numbers, dates, owners, systems, budgets, risks, timelines).
5. Stop only when the user confirms: "Yes, this shared understanding is accurate."

## Interrogation lenses (use all that apply)

Cover these dimensions explicitly:

1. Objective and outcomes: what success means, measurable targets, business value.
2. Current state: existing process, technology stack, pain points, baseline metrics.
3. Scope and boundaries: what is in/out, interfaces, dependencies.
4. Stakeholders and decisions: sponsors, operators, approvers, users, detractors.
5. Constraints: budget, timeline, compliance, security, procurement, skills.
6. Risks and failure modes: delivery, adoption, operations, legal, reputational.
7. Operating model: governance, ownership, support, change management.
8. Delivery path: phases, milestones, quick wins, sequencing, cutover strategy.

## Deep Discovery Resources

For comprehensive discovery frameworks and question banks, read:

- **Discovery frameworks**: `$SKILL_DIR/references/frameworks.md`
  - 5 Whys (root cause analysis)
  - Pre-mortem analysis (risk identification)
  - First principles thinking
  - Assumption surfacing and validation

- **Question bank**: `$SKILL_DIR/references/question-bank.md`
  - 200+ questions across all 8 interrogation lenses
  - Forcing specificity, uncovering contradictions, exploring edge cases

- **Domain-specific guides** (read when topic matches):
  - Contact centres: `$SKILL_DIR/references/domains/contact-centre.md`
  - Salesforce: `$SKILL_DIR/references/domains/salesforce-implementation.md`
  - Cloud migration: `$SKILL_DIR/references/domains/cloud-migration.md`
  - Digital transformation: `$SKILL_DIR/references/domains/digital-transformation.md`

## Output contract

Maintain these artifacts during the interview:

1. **Working document** (updated after each round):
   - `./tmp/ibm-grill-me-shared-understanding-v{N}.md`
   - Increment version number with significant updates (start at v1)

2. **Question log** (append-only):
   - `./tmp/ibm-grill-me-questions-{YYYY-MM-DD}.md`
   - Timestamp each round, track which assumptions were validated/invalidated

3. **Final deliverables** (when alignment confirmed):
   - `./outputs/shared-understanding-{topic}-{date}.md`
   - `./outputs/discovery-visuals-{date}.png` (run visualization script)

To generate visualizations after creating shared understanding:

```bash
python3 $SKILL_DIR/scripts/visualize-discovery.py ./tmp/ibm-grill-me-shared-understanding-v{N}.md

Only copy to outputs/ when the user confirms alignment.

Use this exact structure:

# Shared Understanding: <initiative name>

## 1. Problem Statement
- ...

## 2. Desired Outcomes (Measurable)
- ...

## 3. Current State Summary
- ...

## 4. In Scope / Out of Scope
- In scope: ...
- Out of scope: ...

## 5. Stakeholders and Decision Rights
- ...

## 6. Constraints and Non-Negotiables
- ...

## 7. Risks and Open Questions
- Risks:
  - ...
- Open questions:
  - ...

## 8. Assumptions to Validate
- ...

## 9. Proposed Work Plan Shape (Not final solution)
- ...

## 10. Alignment Check
- Confirmed by user: Yes/No
- Date: <YYYY-MM-DD>

Quality assessment before exit

Score each dimension (1-5) before exiting:

┌─────────────────────┬───────┬─────────────────────────────────────────────────────────────┐
│      Dimension      │ Score │                          Criteria                           │
├─────────────────────┼───────┼─────────────────────────────────────────────────────────────┤
│ Problem clarity     │ 1-5   │ 5: Testable hypothesis. 3: Directionally clear. 1: Vague    │
├─────────────────────┼───────┼─────────────────────────────────────────────────────────────┤
│ Stakeholder mapping │ 1-5   │ 5: Decision rights + metrics per role. 1: Just names        │
├─────────────────────┼───────┼─────────────────────────────────────────────────────────────┤
│ Constraints         │ 1-5   │ 5: Validated, quantified, sourced. 1: Assumed               │
├─────────────────────┼───────┼─────────────────────────────────────────────────────────────┤
│ Risk assessment     │ 1-5   │ 5: Likelihood × impact + mitigation. 1: Generic list        │
├─────────────────────┼───────┼─────────────────────────────────────────────────────────────┤
│ Success criteria    │ 1-5   │ 5: Leading/lagging metrics with thresholds. 1: Aspirational │
└─────────────────────┴───────┴─────────────────────────────────────────────────────────────┘

Exit criteria:
- Average score ≥ 4.0
- No dimension < 3
- User confirms alignment check as "Yes" in section 10

If any criterion fails, continue questioning.