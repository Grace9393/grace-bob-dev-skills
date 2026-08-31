# IBM Agentic Pattern Catalog

Last updated: 2026-03-04 (refactored from embedded catalog)

Use this file when validating architecture decisions against IBM Agentic Enterprise patterns.

## Core Orchestration Patterns

### 1. Centralized Coordinator Pattern
When to use:
- Simple workflows with fewer than 5 agents
- Clear sequential dependencies
- Low-latency requirements (under 3 seconds)
- Single decision point required

Characteristics:
- Single orchestrator controls workflow and state
- Agents report to coordinator
- Synchronous communication is common

Trade-offs:
- Pros: easy debugging, centralized error handling, clear visibility
- Cons: single point of failure, scaling bottleneck, coordinator complexity

IBM recommendation:
- Good default for small and medium enterprise systems
- Add redundancy before production

### 2. Distributed Choreography Pattern
When to use:
- Complex workflows with more than 10 agents
- High autonomy requirements
- Event-driven architecture
- No central bottleneck is acceptable

Characteristics:
- Agents coordinate through events/messages
- No central orchestrator
- Asynchronous communication

Trade-offs:
- Pros: high scalability, high resilience, flexible workflow evolution
- Cons: harder debugging, eventual consistency complexity, harder end-to-end visibility

IBM recommendation:
- Use at larger scale (for example, over 100K requests/day)
- Requires mature observability

### 3. Hierarchical Coordination Pattern
When to use:
- Very large systems (more than 20 agents)
- Clear domain boundaries
- Multiple sub-workflows

Characteristics:
- Meta-coordinator and domain coordinators
- Domain-based grouping
- Coordinators communicate peer-to-peer

Trade-offs:
- Pros: scales for large estates, enables parallel domain workflows
- Cons: coordination overhead, complex cross-domain orchestration, added latency depth

IBM recommendation:
- Reserve for enterprise-scale systems (for example, over 50 agents)

## Agent Design Patterns

### 1. Specialist Agent Pattern
Description:
- One clear capability per agent

IBM standard:
- Agent role should fit one sentence
- Prefer 3 to 8 tools/capabilities per agent (avoid over 15)
- Explicit input/output contracts
- Autonomous decisions within domain boundaries

### 2. Cognitive Agent Pattern
Description:
- Agents with reasoning, memory, and planning capabilities

IBM standard:
- Keep context window utilization below 60 percent
- Define short-term and long-term memory strategies
- Graceful degradation when context or memory limits are reached

### 3. Reactive Agent Pattern
Description:
- Event-driven agents with minimal reasoning

IBM standard:
- Sub-second response target
- Stateless where practical
- Idempotent operations

## Communication Patterns

### 1. Request-Reply Pattern
IBM standard:
- Timeout: max 30 seconds (3 seconds preferred)
- Retry: 3 attempts with exponential backoff
- Circuit breaker: trigger at 50 percent error rate

### 2. Publish-Subscribe Pattern
IBM standard:
- Versioned schemas
- Dead-letter queue for failed events
- At-least-once delivery guarantee

### 3. Message Queue Pattern
IBM standard:
- Queue depth monitoring (target under 1000)
- Consumer autoscaling based on depth
- Message TTL defined (24 hours default)

## Data Management Patterns

### 1. Database-per-Service Pattern
IBM standard:
- Preferred for microservice-style agents
- Use saga patterns for distributed transactions
- Keep event history for auditability

### 2. Shared Memory Pattern
IBM standard:
- Suitable for read-heavy shared context
- Apply TTL to cached values
- Define cache invalidation strategy

### 3. Event Sourcing Pattern
IBM standard:
- Append-only event log
- Replay support for recovery
- Snapshot cadence for performance

## Resilience Patterns

### 1. Circuit Breaker Pattern
IBM standard:
- Open circuit after 50 percent error rate over 1 minute
- Half-open after 60 seconds
- Close after 5 successful probes

### 2. Retry with Backoff Pattern
IBM standard:
- 3 retries max
- Exponential backoff: 1s, 2s, 4s
- Add jitter to avoid synchronized retries

### 3. Saga Pattern
IBM standard:
- Compensating transactions required
- Idempotent actions required
- Overall saga timeout defined (5 minutes default)

## Security Patterns

### 1. Zero Trust Agent Pattern
IBM standard:
- Authentication and authorization on every inter-agent call
- JWT tokens with 1-hour expiration
- Service-to-service mTLS
- Audit logs for all critical actions

### 2. Secret Management Pattern
IBM standard:
- Centralized secret store (for example, Vault)
- Secret rotation every 90 days
- No secrets in logs or errors

## Observability Patterns

### 1. Distributed Tracing Pattern
IBM standard:
- OpenTelemetry-compatible tracing
- Trace ID propagated in all inter-agent calls
- Sampling: 100 percent errors, 10 percent successful flows

### 2. Structured Logging Pattern
IBM standard:
- JSON logs
- Required fields: timestamp, trace_id, agent_id, action, result
- PII redaction required
