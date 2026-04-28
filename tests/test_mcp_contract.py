from experiment_os.domain.schemas import BriefRequest, RunEventInput, RunStartInput
from experiment_os.services.event_contract import AgentEventContract
from experiment_os.services.metrics import MetricsExtractor
from experiment_os.services.protocol import AgentWorkProtocol
from experiment_os.services.runs import RunRecorder
from experiment_os.repositories.runs import RunRepository


def test_mcp_agent_contract_preserves_dependency_presentation(session):
    protocol = AgentWorkProtocol(session).start(
        request=BriefRequest(
            task="Fix Python SDK API drift wrapper failure",
            libraries=["example-llm-sdk", "python"],
            agent="codex",
            toolchain="shell",
        ),
        run=RunStartInput(
            task="MCP compliance regression",
            agent="codex",
            toolchain="mcp",
        ),
    )

    context = protocol["agent_work_context"]
    presentation = context["presentation_contract"]

    assert protocol["run"]["run_id"]
    assert presentation["must_load"]
    assert presentation["dependsOn"]
    assert presentation["decision_rules"]
    assert context["known_failures"]
    assert "knowledge.python-api-drift-local-shim" in context["required_load_order"]


def test_mcp_event_contract_and_metrics_require_final_answer_recording(session):
    contract = AgentEventContract().as_dict()
    recorder = RunRecorder(session)
    run = recorder.start_run(
        RunStartInput(
            task="MCP event recording regression",
            agent="codex",
            toolchain="mcp",
        )
    )

    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="mcp_tool_called",
            payload={"server": "experiment_os", "tool": "start_pre_work_protocol"},
        )
    )
    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="mcp_tool_called",
            payload={"server": "experiment_os", "tool": "get_agent_dependency_graph"},
        )
    )
    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="mcp_tool_called",
            payload={
                "server": "experiment_os",
                "tool": "record_run_event",
                "recorded_event_type": "final_answer",
            },
        )
    )

    events = RunRepository(session).list_events(run["run_id"])
    metrics = MetricsExtractor().extract(events)

    assert "final_answer" in [
        event["type"] for event in contract["event_types"]
    ]
    assert metrics["mcp_pre_work_protocol_called"] is True
    assert metrics["mcp_dependency_graph_loaded"] is True
    assert metrics["mcp_final_answer_recorded"] is True
