# Agent Adapter Layer

Experiment OS runs experiments through a small adapter boundary:

- `AgentRunRequest` describes workdir, prompt, environment, and timeout.
- `AgentExecutionResult` captures command, stdout, stderr, exit code, duration, and transcript.
- adapter implementations translate that contract into a specific agent CLI invocation.

Current adapters:

- `CodexCliAdapter` for `codex exec --json`;
- `ShellAgentAdapter` for deterministic fixture commands;
- `ExternalCliAdapter` for configurable one-shot CLIs;
- `AiderCliAdapter` as an Aider profile over `ExternalCliAdapter`;
- `OpenCodeCliAdapter` as an OpenCode profile over `ExternalCliAdapter`.

The adapter boundary is also where MCP protocol enforcement lives. A prompt can ask an agent to
call MCP tools, but it cannot prove that the tool surface is available or that the dependency graph
was loaded before editing. `AgentPreWorkGate` wraps agent execution:

1. call Experiment OS pre-work protocol before the agent receives the task;
2. inject the resulting agent work context as prompt/artifact input;
3. run the target agent adapter;
4. record final answer, verification, and compliance status after the run.

Dashboard and matrix metrics should report task success separately from protocol compliance.

Matrix condition roles:

- `static_brief`: context is injected as text, but protocol compliance is not enforced.
- `mcp_brief`: the agent is asked to use MCP tools itself.
- `gated_brief`: Experiment OS loads context before agent execution and records compliance events.
- `opencode_gated_brief`: same gate, different agent backend.
