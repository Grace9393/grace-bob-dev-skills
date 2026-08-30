# Architecture Assessment Dimensions

Use this file when scoring architecture quality and explaining findings by domain.

## Eight Dimensions

### 1. Agent Design and Decomposition
Evaluate:
- Autonomy and boundary clarity
- Specialization and capability fit
- Decomposition granularity
- Reasoning/memory architecture fit
- Tool and contract clarity

### 2. Orchestration and Coordination
Evaluate:
- Coordination model fit (centralized, distributed, hierarchical)
- Workflow design (adaptive vs rigid)
- Decision authority placement
- Failure detection and recovery design
- Workflow state management

### 3. Communication and Messaging
Evaluate:
- Protocol and pattern fit
- Message schema quality and versioning
- Sync/async appropriateness
- Error propagation strategy
- Traceability and diagnosability

### 4. Data and Knowledge Management
Evaluate:
- Shared state model
- Data ownership and sovereignty
- Context propagation efficiency
- Memory architecture design
- Consistency guarantees

### 5. Scalability and Performance
Evaluate:
- Independent scaling ability
- Load distribution
- Bottleneck risk
- Resource efficiency
- Caching strategy fitness

### 6. Resilience and Reliability
Evaluate:
- Fault isolation and containment
- Circuit breaker/retry quality
- Degraded operation capability
- Recovery pathways and runbooks

### 7. Security and Governance
Evaluate:
- Authentication/authorization controls
- Secrets and key management
- Data protection and encryption
- Auditability and policy enforcement

### 8. Observability and Operations
Evaluate:
- Logging quality
- KPI and SLO metrics coverage
- End-to-end tracing
- Production debugging readiness
- Alerting and operational response

## Maturity Scoring Rubric

Use a 1-5 scale per dimension:
- 1 Ad Hoc: fragmented, likely to fail under load or change
- 2 Basic: some structure but major gaps remain
- 3 Developing: workable baseline with clear improvement opportunities
- 4 Mature: strong implementation and consistent best practices
- 5 Optimized: production-grade, measurable, and continuously improved

## Rating Guidance

- Always include evidence for each score.
- If critical information is missing, score conservatively and state assumptions.
- Tie each low score to prioritized recommendations.
