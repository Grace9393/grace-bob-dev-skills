---
name: bob-onboarding
description: Get IBM Bob (IBM internal AI coding assistant) access - waitlist signup, regional constraints, pricing for client engagements, and what to do while waiting.
---

# bob-onboarding

Use when an IBM Consulting employee asks how to get Bob, what Bob can do, or what to use while waiting for access.

## What Bob is
IBM Bob (Bob@IBM) is IBM Consulting's internal AI-powered coding assistant. GA was announced **2026-03-24**. Bob features specialized **modes** for different development tasks (architect, code-review, etc. — see `coding-agent-mode`).

> ⚠️ **IBM internal use only.** Eligibility: IBM Consultants doing consulting asset development, PoCs, or client demos, who commit to providing usage feedback.

## Get access (4 steps, ~24 hours)

1. **Visit waitlist**: <https://w3.ibm.com/w3publisher/bob>
2. **Sign up** with IBM credentials.
3. **Wait** — access typically granted within 24 hours; notification by IBM email.
4. **Receive** credentials, setup instructions, doc links, and Slack channel invite.

## Slack support
Join `#guild-coding-agents-at-consulting` on IBM Enterprise Slack — questions, updates, and community support.

## Regional constraint

> ⚠️ Bob's backend LLM is currently **US region only**. Confirm your engagement's data-residency rules permit US-region processing **before** using Bob on client material.

## Client engagements (selling Bob + IBMC services)

For paid client work involving Bob:
- Follow the **Bob Sales Process and Guidelines** on Seismic.
- Pricing: **SaaS plans** are documented on Seismic.
- Contact: Jerry Liu (`liutao@us.ibm.com`).
- Client preview: nominate the client via the Microsoft Form linked from the Bob landing page.

(Direct links live on the IBM Bob@Consulting landing page; this skill avoids hardcoding click-tracked URLs.)

## What to do while waiting for access

You can get a Bob-equivalent experience now using **Cline** + **IBM Consulting Advantage (ICA)** API key — Cline is open source and uses your ICA models directly. See `cline-with-ica`.

After Bob access lands, switching is near-effortless if you've been working in Cline already.

## Bobalytics

Once onboarded, your usage feeds the **Bobalytics** dashboard (admin-prod URL on the Bob landing). Useful for:
- Personal usage retrospective
- Team-level adoption KPIs
- Engagement reporting (consultant time saved, etc.)

## Related skills
- `cline-with-ica` — recommended bridge while waiting for Bob, and a fine permanent option.
- `coding-agent-mode` — Bob's specialized modes pattern.
- `ica-api` — generate the API key Cline needs.
