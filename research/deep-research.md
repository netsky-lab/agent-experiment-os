# Deep Research: MCP-Native Experiment Knowledge System

Date: 2026-04-26

## Executive Claim

This repo should not be designed as a Mem0/Zep-style agent memory product, an eval dashboard, or a trace viewer.

The technically defensible direction is:

> A research system for converting coding-agent work into reusable experimental knowledge: source-backed issue learnings, structured run traces, failure taxonomies, intervention evidence, and MCP-delivered work briefs.

The product primitive is not "memory". The product primitive is an **experiment knowledge object**:

```text
context -> claim/evidence -> run -> observed failure -> diagnosis -> intervention -> measured effect -> reusable policy
```

The agent-facing artifact is not a long memory dump. It is a **work brief**:

```text
Given this repo, task, libraries, agent, model, and toolchain:
- what failures have occurred before?
- what current issues/docs are relevant?
- what interventions have evidence?
- what checks should the agent perform before editing?
- what should the agent avoid?
```

## Why This Is Not Mem0 or Zep

Mem0/Zep/Letta-style systems are designed around persistent agent memory: facts, preferences, summaries, entities, conversations, temporal updates, and retrieval into future context.

That is a different system class.

This project needs a different technical center:

| Generic agent memory | Experiment knowledge system |
| --- | --- |
| Stores memories | Stores evidence-backed claims and experimental outcomes |
| Optimizes recall relevance | Optimizes decision usefulness before and after agent work |
| Often vector-first | Typed evidence graph first, vector search second |
| User/session continuity | Hypothesis/run/failure/intervention/policy lifecycle |
| Memory can be auto-written | High-impact policy requires promotion/review |
| Retrieval answers "what is relevant?" | Brief answers "what should the agent do differently?" |
| Facts/preferences decay or update | Policies carry applicability, confidence, counterexamples, and expiry |

So the architecture should not begin with a generic memory table and embeddings. It should begin with:

- source snapshots,
- extracted issue claims,
- structured run events,
- failure labels,
- interventions,
- policy candidates,
- human-reviewed policy records,
- brief compilation.

Vector search can help retrieve candidates, but it is not the source of truth.

## Research Basis

### Failure Diagnosis Is a Real Research Gap

Recent work supports the core premise that aggregate success rates are too shallow.

`2602.02475` AgentRx frames failed agent runs as long-horizon, tool-mediated trajectories where the hard problem is localizing the critical failure step and category. That maps directly to our need for `failure.evidence`, `failure.critical_step`, and auditable diagnosis logs.

`2509.25370` Where LLM Agents Fail and How They can Learn From Failures introduces modular agent failure taxonomy and targeted feedback. This supports a system that separates memory, planning, action, reflection, and system-level failures instead of storing undifferentiated "lessons".

`2509.13941` An Empirical Study on Failures in Automated Issue Solving analyzes failed SWE-Bench-Verified instances and derives phase/category/subcategory failure modes. This is directly aligned with our coding-agent domain.

`2511.00197` Understanding Code Agent Behaviour shows that success/failure should be studied through trajectories, not only final patches. It also supports tracking context-gathering and validation behavior.

`2604.02547` Beyond Resolution Rates explicitly argues that resolution rate hides the behavioral structure of success and failure. This supports our UI emphasis on timelines, behavioral markers, and policy impact, not only score charts.

`2603.05941` XAI for Coding Agent Failures supports transforming raw execution traces into structured explanations and actionable recommendations. That is close to our "run report -> policy candidate" step, but our project goes further by feeding approved learnings back to future agents.

`2601.15195` Where Do AI Coding Agents Fail? uses real agent-authored GitHub PRs and rejection patterns. This validates that real-world agent failure includes CI, review, duplicate work, misalignment, and social/project context, not just code correctness.

### Agent Failures Are Often Environment/Protocol Failures

The project should explicitly model failures outside the base model.

`2508.19504` Aegis shows that agent success can improve through environment optimizations without changing the agent or LLM. This supports interventions such as better observability, command normalization, tool-call repair, and issue/docs prefetch.

`2602.09937` Cloud RCA failure analysis finds that failures can persist across model tiers and originate from shared agent architecture, communication, or environment interaction. This supports our distinction between model failure, framework failure, tool-interface failure, and knowledge-context failure.

This matters for positioning: the system should not only say "model X is worse". It should identify whether the failure comes from:

- stale external knowledge,
- missing project context,
- tool schema mismatch,
- insufficient validation,
- environment opacity,
- bad intervention,
- wrong task decomposition,
- project workflow mismatch.

### Structured Observability Is Necessary but Not Sufficient

`2602.10133` AgentTrace supports structured operational/cognitive/contextual logging. It gives us the substrate.

But observability alone does not produce a reusable rule. Our project adds:

- issue-derived knowledge cards,
- failure taxonomies,
- intervention records,
- before/after metrics,
- policy promotion,
- MCP brief compilation.

So the relationship is:

```text
structured traces are input data
experiment knowledge is the derived artifact
work brief is the agent-facing output
```

### Benchmarks Need to Look Like Real Agent Work

`2510.08996` Saving SWE-Bench argues that GitHub issue benchmark descriptions differ from how developers actually ask coding assistants for help. This supports using realistic user-task briefs, not only formal benchmark issues.

`2504.02605` Multi-SWE-bench and `2504.08703` SWE-PolyBench support multilingual, repository-level issue solving rather than Python-only toy tasks.

`2602.09540` SWE-Bench Mobile shows that industrial mobile tasks are much harder and that agent design matters. This supports capturing agent/framework/toolchain metadata as first-class dimensions.

Therefore, our research evaluation should not only run SWE-Bench-style issue solving. It should also mutate tasks into realistic chat instructions and compare:

- baseline agent,
- agent + docs context,
- agent + issue knowledge,
- agent + issue knowledge + prior failure/intervention policies.

### MCP Is the Right Agent Interface, but Needs Production Discipline

`2505.02279` positions MCP as the tool/context protocol among emerging agent protocols.

`2511.20920`, `2602.01129`, and `2603.13417` show that MCP introduces production and security concerns: identity, scoped authorization, provenance, prompt injection, tool poisoning, audit logs, structured errors, timeouts, and observability.

This supports MCP-first design, but not naive MCP design.

Required system properties:

- every issue-derived card has source provenance,
- every policy has evidence and reviewer status,
- external issue content is treated as untrusted,
- MCP tools are read-mostly by default,
- write tools are scoped to run/event recording,
- policy promotion is separate from observation recording,
- brief content is compact, source-linked, and confidence-labeled.

### Memory Research Is Useful Only as Contrast

`2603.07670`, `2602.11243`, and `2507.05257` show that memory systems need write/read/manage loops, structure, selective forgetting, and evaluation.

We should borrow these engineering concerns:

- write filtering,
- contradiction handling,
- selective retrieval,
- memory structure,
- evaluation over multiple interactions.

But the project should not optimize for generic memory benchmarks. It should optimize for:

- fewer repeated failure modes,
- better pre-edit decisions,
- faster recovery after failures,
- more accurate issue-derived workarounds,
- stronger policy precision.

## System Design

### Core Loop

```text
1. Agent receives task.
2. Agent calls MCP get_work_brief.
3. Brief compiler retrieves:
   - relevant issue cards,
   - relevant docs cards,
   - prior runs,
   - failure patterns,
   - approved policies,
   - known counterexamples.
4. Agent works and records structured events.
5. Analyzer creates run report:
   - outcome,
   - failure candidates,
   - critical steps,
   - evidence pointers,
   - intervention candidates.
6. Human reviews proposed cards/policies.
7. Approved policies affect future briefs.
```

The system learns only when evidence survives review or repeated validation.

### MCP Tools

Agent-facing tools:

```text
get_work_brief(task, repo, libraries, agent, model, toolchain, token_budget)
search_issue_knowledge(library, topic, version?, ecosystem?)
search_experiment_knowledge(query, filters)
record_run_start(metadata)
record_run_event(run_id, event)
record_failure(run_id, failure)
record_intervention(run_id, intervention)
record_metric(run_id, metric)
summarize_run(run_id)
propose_policy(source_ids)
```

MCP resources:

```text
experiment://failure-taxonomy
experiment://policies/{policy_id}
experiment://knowledge-cards/{card_id}
experiment://runs/{run_id}
experiment://briefs/{brief_id}
```

MCP prompts:

```text
pre_work_research
failure_diagnosis
post_run_learning
policy_promotion
issue_claim_extraction
```

The prompt layer matters because it makes the workflow opinionated. The agent should be guided to research known issues before editing code that depends on a library.

### Data Model

#### Source Snapshot

External or internal evidence unit.

Fields:

- `id`
- `source_type`: `github_issue`, `github_pr`, `docs`, `run_trace`, `test_output`, `human_note`
- `url`
- `retrieved_at`
- `content_hash`
- `repository`
- `library`
- `version_range`
- `trust_level`
- `raw_content_ref`

#### Claim

A normalized assertion extracted from a source.

Examples:

- "drizzle-kit version X emits unstable defaults for Y pattern"
- "OpenCode + Gemma often emits invalid tool-call JSON under shell quoting pressure"
- "Maintainers reject large agent PRs more often than narrow PRs"

Fields:

- `claim_type`: `problem`, `symptom`, `workaround`, `version_note`, `failure_pattern`, `maintainer_preference`
- `statement`
- `source_ids`
- `confidence`
- `status`: `unreviewed`, `accepted`, `rejected`, `superseded`
- `contradicts_claim_ids`

#### Knowledge Card

Human-readable compression of related claims.

Fields:

- `problem`
- `symptoms`
- `affected_versions`
- `workarounds`
- `verification_status`
- `source_ids`
- `last_verified_at`
- `confidence`

#### Experiment

Fields:

- `hypothesis`
- `task_family`
- `repo_type`
- `libraries`
- `agent`
- `model`
- `toolchain`
- `design`
- `expected_observations`

#### Run

Fields:

- `experiment_id`
- `task`
- `repo_ref`
- `agent`
- `model`
- `toolchain`
- `started_at`
- `ended_at`
- `outcome`
- `trace_ref`
- `patch_ref`
- `metrics`

#### Event

Structured trace event.

Fields:

- `run_id`
- `step_index`
- `event_type`: `thought`, `tool_call`, `tool_result`, `file_edit`, `test_run`, `error`, `retry`, `final`
- `payload`
- `source_ref`

#### Failure

Fields:

- `run_id`
- `taxonomy_label`
- `critical_step`
- `evidence_event_ids`
- `severity`
- `root_cause`
- `confidence`

Initial taxonomy:

- stale library knowledge
- issue-knowledge miss
- retrieval miss
- planning failure
- context-gathering failure
- wrong file localization
- wrong edit
- tool-call syntax failure
- shell escaping failure
- environment mismatch
- test hallucination
- premature completion
- loop / cognitive deadlock
- over-repair
- under-specification
- review/project misalignment

#### Intervention

Fields:

- `failure_id`
- `intervention_type`
- `description`
- `before_metrics`
- `after_metrics`
- `applicability_conditions`
- `side_effects`
- `confidence`

Examples:

- issue prefetch
- docs version pinning
- command normalization
- smaller tool steps
- tool-call JSON validation
- retry with minimal diff
- require tests before final answer
- add project activity scan before PR
- enforce narrow patch scope

#### Policy

Human-approved reusable rule.

Fields:

- `condition`
- `recommendation`
- `rationale`
- `evidence_ids`
- `counterexample_ids`
- `confidence`
- `reviewer`
- `status`
- `expires_at`

Example:

```text
Condition:
repo_type=python_cli AND agent=opencode AND model=gemma

Recommendation:
Use single-purpose shell commands and validate tool-call JSON before execution.

Evidence:
7 prior runs; 4 failures reduced after command normalization.

Confidence:
medium
```

### Brief Compiler

The brief compiler is the key differentiator.

Inputs:

- task text,
- repo metadata,
- dependency/language detection,
- agent/model/toolchain,
- user constraints,
- token budget.

Retrieval stages:

```text
1. Detect libraries, frameworks, repo type, task family.
2. Retrieve accepted policies by exact dimensions.
3. Retrieve knowledge cards by library/topic/version.
4. Retrieve similar prior runs by repo/task/failure features.
5. Retrieve counterexamples and expired/stale warnings.
6. Rank by applicability, recency, source quality, confidence, and severity.
7. Emit compact work brief with links, not raw dumps.
```

Output shape:

```json
{
  "brief_id": "...",
  "known_risks": [
    {
      "risk": "stale library API assumption",
      "why_relevant": "task touches drizzle migrations",
      "confidence": "medium",
      "sources": ["..."]
    }
  ],
  "recommended_checks": [
    "Inspect installed package version before editing schema",
    "Search project migration conventions before hand-editing generated files"
  ],
  "recommended_interventions": [
    {
      "intervention": "issue prefetch",
      "condition": "library behavior differs across minor versions",
      "evidence": ["policy:..."]
    }
  ],
  "avoid": [
    "Do not rewrite unrelated migration history without existing project precedent"
  ]
}
```

## Issue Knowledge Ingestion

The issue layer should not be a search wrapper. It should create structured, source-backed cards.

Pipeline:

```text
GitHub search/query
-> source snapshot
-> claim extraction
-> claim clustering
-> contradiction detection
-> version/status extraction
-> knowledge card draft
-> human review or run-based validation
-> accepted/rejected/superseded card
```

Issue cards should distinguish:

- maintainer-confirmed workaround,
- user speculation,
- version-specific regression,
- closed as duplicate,
- fixed by PR,
- unresolved discussion,
- outdated workaround.

The agent should never be told "do this because an issue said so." It should be told:

```text
This issue cluster suggests X. Confidence: low/medium/high.
Evidence: maintainer confirmed / multiple users / linked PR / unverified.
Recommended check: verify installed version and run tests.
```

## UI/UX Design

The UI is not a generic dashboard. It is a curation surface for knowledge that agents will consume.

Required screens:

### Agent Brief Preview

Shows exactly what `get_work_brief` will return.

This is the most important product screen because it validates whether the system's knowledge is actually useful before it enters the agent context.

### Knowledge Cards

Cards extracted from issues/docs/runs:

- problem,
- symptoms,
- affected versions,
- workaround,
- evidence,
- confidence,
- review status.

### Failure Atlas

Taxonomy browser:

- failure label,
- examples,
- affected agents/models/toolchains,
- linked interventions,
- unresolved questions.

### Intervention Library

Evidence-backed interventions:

- what it changes,
- which failures it targets,
- before/after metrics,
- applicability,
- side effects.

### Experiment Timeline

Displays:

```text
hypothesis -> design -> run -> failure -> diagnosis -> intervention -> metric movement -> policy
```

### Policy Review Queue

Human approval surface:

- proposed policy,
- evidence,
- counterexamples,
- likely blast radius,
- approve/edit/reject.

## MVP

The MVP should be narrow: coding-agent work on real repositories with issue-sensitive dependencies.

### Build First

1. MCP server with `get_work_brief`, `search_issue_knowledge`, and run recording.
2. GitHub issue ingestor for selected libraries/repos.
3. Source snapshot + claim + knowledge card schema.
4. Run/event/failure/intervention schema.
5. Simple UI for brief preview, knowledge cards, runs, and policy review.
6. Evaluation harness for baseline vs brief-assisted agents.

### Do Not Build First

- generic personal memory,
- full Langfuse replacement,
- broad eval platform,
- autonomous policy promotion,
- universal vector knowledge base,
- complex multi-agent orchestration.

## Evaluation Plan

### Research Questions

RQ1: Do issue-derived work briefs reduce stale-library and wrong-workaround failures?

RQ2: Do prior failure/intervention policies reduce repeated failures in similar repo/task/toolchain conditions?

RQ3: Does structured run capture improve failure attribution compared with raw transcripts?

RQ4: Does human-reviewed policy promotion produce higher precision than automatic memory writes?

### Experimental Conditions

For each coding task:

```text
A. baseline agent
B. agent + docs-only context
C. agent + issue-derived knowledge cards
D. agent + issue cards + prior failure/intervention policies
```

### Task Families

Good first task families:

- package migration bugs,
- ORM migration quirks,
- frontend framework version changes,
- Playwright/browser environment failures,
- ESM/CJS config failures,
- MCP tool schema failures,
- test fixture mismatch bugs.

### Metrics

- task success,
- patch correctness,
- tests passing,
- invalid tool calls,
- stale API usage,
- repeated failure rate,
- retries to valid patch,
- wrong file edits,
- over-repair count,
- token cost,
- wall-clock time,
- human review burden,
- policy usefulness on later runs.

## Technical Stance

Use typed storage as the core:

- Postgres for canonical entities and relationships.
- Full-text search for issues/docs.
- Optional embeddings for recall candidates, never as source of truth.
- Object storage/filesystem for raw snapshots and traces.
- Background workers for ingestion, extraction, clustering, and diagnosis.
- MCP server for agent-facing tools/prompts/resources.
- HTTP API for UI and integrations.

The important technical decision:

> Retrieval should return candidates. Policy selection should be typed, source-backed, confidence-aware, and auditable.

## Security and Trust Constraints

Issue content and docs can carry prompt injection or misleading instructions. The system must treat external text as evidence, not instruction.

Controls:

- source provenance on every card,
- retrieved-at timestamps and content hashes,
- issue text sanitized before brief inclusion,
- no external commands copied into "recommended action" without review,
- scoped MCP write tools,
- audit log for all policy promotion,
- confidence and status on every card,
- counterexamples and expiry for policies.

## Final Positioning

Best short framing:

> Experiment knowledge for coding agents.

More precise:

> An MCP-native research system that turns issue knowledge and agent run traces into failure-aware, intervention-backed work briefs.

The defensible novelty is the closed loop:

```text
issues/docs/runs -> claims -> failure diagnosis -> interventions -> reviewed policies -> MCP work brief -> better next run
```

That loop is meaningfully different from evals, observability, and generic memory.

