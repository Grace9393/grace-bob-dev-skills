# Quantitative Validation Thresholds

Use these thresholds to make findings measurable and to prioritize recommendations.

## Agent Composition
- Optimal: 3-8 agents
- Warning: over 12 agents
- Critical: over 20 agents
- Check for consolidation opportunities when over 15

## Orchestration Complexity
- Optimal: workflow explainable in under 500 words
- Warning: needs over 1000 words
- Critical: not clearly explainable end-to-end

## LLM Context Utilization
- Optimal: under 60 percent
- Warning: 60-80 percent
- Critical: over 80 percent

## API Call Efficiency per Workflow
- Optimal: under 5 calls
- Warning: 5-10 calls
- Acceptable: 10-20 calls only with parallelization
- Critical: over 20 calls, or sequential depth over 5

## Retry/Error Recovery
- Optimal: under 3 percent retry rate
- Warning: 3-5 percent
- Acceptable: 5-10 percent with robust backoff/jitter
- Critical: over 10 percent

## Response Time Targets
- Interactive workflows: under 3 seconds
- Background workflows: under 30 seconds
- Warning: 30-60 seconds
- Critical: over 60 seconds

## Database Connection Pooling
- Optimal: pool size around 2x expected concurrent agent count
- Warning: pool smaller than expected concurrency
- Critical: no pooling strategy
