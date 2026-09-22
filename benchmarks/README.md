# Nippan Benchmarks

Benchmark before selecting permanent models or adding expensive infrastructure.

Primary specification:
- `BENCHMARK_SPEC_V1.md`

Primary decision metric:
- **cost per successful task**

Required dimensions include:
- Thai intent/classification accuracy
- Jev and low-cost router comparison
- conversational continuity
- structured output validity
- tool-call correctness
- retrieval and memory quality
- privacy/policy compliance
- Context Compiler fidelity when evaluated
- latency p50/p95
- retry/fallback rate
- token usage and model/provider cost

Model IDs belong in benchmark configuration/policy, not application code.
