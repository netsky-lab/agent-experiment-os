# Paper Corpus

Primary corpus scope: 2025-2026 papers relevant to coding-agent failure analysis, trajectory diagnosis, MCP production/security, software-agent benchmarks, and memory evaluation as a contrast class.

For every PDF, the arXiv abstract page is `https://arxiv.org/abs/<paper-id>` and the canonical PDF is `https://arxiv.org/pdf/<paper-id>`.

The corpus intentionally excludes older memory/reflection papers from the primary design basis. Those papers can be useful historical background, but this repo should be grounded in the current coding-agent and MCP ecosystem.

## Failure Taxonomy and Diagnosis

| Paper | Local PDF | Why it matters |
| --- | --- | --- |
| Where Do AI Coding Agents Fail? An Empirical Study of Failed Agentic Pull Requests in GitHub | `2601.15195_where-do-ai-coding-agents-fail.pdf` | Real-world failed agentic PRs; supports using PR/issue/review outcomes as evidence, not only benchmark scores. |
| AgentRx: Diagnosing AI Agent Failures from Execution Trajectories | `2602.02475_agentrx-diagnosing-agent-failures.pdf` | Supports critical-step localization, evidence-backed failure attribution, and auditable diagnosis logs. |
| Where LLM Agents Fail and How They can Learn From Failures | `2509.25370_where-llm-agents-fail-and-learn.pdf` | Supports modular failure taxonomies and targeted corrective feedback. |
| AgenTracer: Who Is Inducing Failure in the LLM Agentic Systems? | `2509.03312_agentracer-failure-attribution.pdf` | Supports failure attribution across long multi-agent traces and feedback-driven improvement. |
| Why Do AI Agents Systematically Fail at Cloud Root Cause Analysis? | `2602.09937_cloud-rca-agent-failure-analysis.pdf` | Supports process-level failure analysis and the claim that architecture/environment failures are not just model weakness. |
| An Empirical Study on Failures in Automated Issue Solving | `2509.13941_automated-issue-solving-failures.pdf` | Directly relevant to SWE-Bench issue solving; supports phase/category/subcategory failure modeling. |
| Understanding Code Agent Behaviour: An Empirical Study of Success and Failure Trajectories | `2511.00197_code-agent-success-failure-trajectories.pdf` | Supports trajectory-level comparison between successful and failed coding-agent runs. |
| XAI for Coding Agent Failures: Transforming Raw Execution Traces into Actionable Insights | `2603.05941_xai-for-coding-agent-failures.pdf` | Supports turning raw traces into structured explanations and recommendations. |
| Beyond Resolution Rates: Behavioral Drivers of Coding Agent Success and Failure | `2604.02547_behavioral-drivers-coding-agent-success-failure.pdf` | Supports moving beyond success rate into behavioral patterns, context gathering, validation, and framework/model effects. |
| Aegis: Taxonomy and Optimizations for Overcoming Agent-Environment Failures in LLM Agents | `2508.19504_aegis-agent-environment-failures.pdf` | Supports environment-level interventions that improve agents without changing the model. |
| AgentTrace: A Structured Logging Framework for Agent System Observability | `2602.10133_agenttrace-structured-logging.pdf` | Supports structured traces as substrate for diagnosis, accountability, and monitoring. |

## Coding-Agent Benchmarks and Evaluation Reality

| Paper | Local PDF | Why it matters |
| --- | --- | --- |
| Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving | `2504.02605_multi-swe-bench.pdf` | Supports multilingual issue-resolving as the right evaluation domain. |
| SWE-PolyBench: A multi-language benchmark for repository level evaluation of coding agents | `2504.08703_swe-polybench.pdf` | Supports repository-level, execution-based evaluation and non-Python coverage. |
| Saving SWE-Bench: A Benchmark Mutation Approach for Realistic Agent Evaluation | `2510.08996_saving-swe-bench.pdf` | Supports the claim that formal GitHub issues do not match real chat-based agent work. |
| SWE-Bench Mobile: Can Large Language Model Agents Develop Industry-Level Mobile Applications? | `2602.09540_swe-bench-mobile.pdf` | Supports industrial task complexity and agent/framework differences. |

## MCP Production and Security

| Paper | Local PDF | Why it matters |
| --- | --- | --- |
| A survey of agent interoperability protocols: MCP, ACP, A2A, and ANP | `2505.02279_agent-interoperability-protocols-mcp-acp-a2a-anp.pdf` | Supports MCP as a tool/context protocol and frames where it sits among agent protocols. |
| Securing the Model Context Protocol (MCP): Risks, Controls, and Governance | `2511.20920_securing-mcp-risks-controls-governance.pdf` | Supports provenance, scoped auth, audit logs, and prompt-injection controls. |
| SMCP: Secure Model Context Protocol | `2602.01129_secure-model-context-protocol.pdf` | Supports identity, authentication, policy enforcement, and audit logging for MCP-based systems. |
| Bridging Protocol and Production: Design Patterns for Deploying AI Agents with MCP | `2603.13417_mcp-production-design-patterns.pdf` | Supports structured error semantics, observability, timeouts, and production-readiness around MCP. |

## Memory as Contrast Class

These papers are included because they clarify what this project is not.

| Paper | Local PDF | Why it matters |
| --- | --- | --- |
| Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers | `2603.07670_memory-for-autonomous-llm-agents-survey.pdf` | Useful taxonomy for generic agent memory, but our object is experimental knowledge, not personal/session memory. |
| Evaluating Memory Structure in LLM Agents | `2602.11243_evaluating-memory-structure-in-llm-agents.pdf` | Supports structured organization over flat retrieval, but not sufficient for experiment/policy lifecycle. |
| Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions | `2507.05257_memory-agent-bench.pdf` | Useful for memory evaluation concepts; secondary to failure/intervention evaluation. |
