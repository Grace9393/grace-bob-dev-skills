# Discovery Frameworks

Deep interrogation techniques for building shared understanding.

---

## 5 Whys - Root Cause Analysis

Uncover root causes by asking "why" five times in succession.

### When to use
- Problems with unclear origins
- Repeated failures
- Symptomatic issues that keep recurring
- When stakeholders jump to solutions

### Process

1. State the problem clearly
2. Ask "Why did this happen?"
3. Use the answer as the new problem
4. Repeat 5 times
5. Validate the root cause

### Extended Example: Database Performance

**Problem:** Database queries are slow

**Why 1:** Why are queries slow?
→ Too many JOIN operations across 8 tables

**Why 2:** Why are there so many JOINs?
→ Highly normalized schema (3NF)

**Why 3:** Why did we choose such high normalization?
→ Followed "database best practices" from 2010

**Why 4:** Why are we still using 2010 patterns?
→ No architecture review process

**Why 5:** Why no review process?
→ Team prioritizes features over technical debt

**Root cause:** Lack of dedicated architecture review cycles causes outdated patterns to persist indefinitely.

---

## Pre-Mortem Analysis

Assume the project has failed. Work backwards to identify what went wrong.

### When to use
- Before major initiatives start
- When stakeholders are overly optimistic
- High-stakes projects
- When you sense hidden risks

### Process

1. Set the scene: "It's 6 months from now. The project has failed completely."
2. Individual brainstorm (5 min): Each person writes failure scenarios
3. Share and cluster similar failures
4. Prioritize by likelihood × impact
5. Identify early warning signs
6. Mitigate: What can we do now to prevent these?

### Extended Example: Cloud Migration

**Scenario:** 6 months from now, migration is cancelled. $2M spent, nothing in production.

**Technical failures:**
- Underestimated dependencies; can't move apps without re-arch
- Network latency breaks integrations
- Security blocked deployment 2 weeks before go-live
- Data migration took 10x longer; integrity issues

**Organizational failures:**
- Key engineer left; knowledge loss
- Business units refused downtime; no migration window
- Budget consumed by unexpected egress charges
- Executive sponsor changed priorities

**Early warning signs:**
- Sprint velocity dropping
- Testing schedules slipping
- Escalations increasing
- Budget variance reports

**Mitigations:**
- Create dependency map BEFORE migration
- Run latency tests early
- Engage security in month 1
- Build rollback capability
- Lock in cutover windows upfront

---

## First Principles Thinking

Break down to fundamental truths, strip away assumptions, rebuild from scratch.

### When to use
- Challenging "best practices"
- Over-complicated solutions
- Disruptive innovation
- "We've always done it this way"

### Process

1. Identify core requirement
2. Strip away all assumptions
3. Validate fundamentals vs conventions
4. Rebuild from fundamentals
5. Compare to current approach

### Example: Customer Support

**Conventional:** "We need a ticketing system"

**First Principles:**
- Core requirement: Customers need problems solved fast
- Assumptions to challenge:
  - "Customers must submit tickets" → What if we detect issues proactively?
  - "Agents must respond to every ticket" → What if 70% can be self-service?
  - "Tickets must be in our system" → What if we meet customers where they are?

**Solution:** Prevention + AI deflection + omnichannel + measure resolution not response time

---

## Assumption Surfacing

Explicitly identify and validate all assumptions.

### Categories
- Technical (APIs, performance, compatibility)
- Business (budget, timeline, resources)
- User (behavior, knowledge, environment)
- Process (approval, deployment, maintenance)

### Validation Methods

| Type | How to Validate |
|------|-----------------|
| Technical capability | POC, vendor references, spike |
| Performance | Load testing, benchmarks |
| Data quality | Sample analysis, profiling |
| User behavior | Interviews, analytics |
| Budget | Formal approval |
| Timeline | Resource check |

### Prioritization

**Risk = Impact × Uncertainty**

- High/High → CRITICAL - validate immediately
- High/Low → Important - monitor
- Low/High → Low priority
- Low/Low → Accept

---

## Framework Selection Guide

| Situation | Framework |
|-----------|-----------|
| Recurring problem, unclear cause | 5 Whys |
| High-stakes, optimistic stakeholders | Pre-Mortem |
| Standard solution feels wrong | First Principles |
| Complex project, many unknowns | Assumption Surfacing |

**Pro tip:** Combine frameworks for maximum impact.
