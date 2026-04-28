from experiment_os.domain.schemas import RunEventInput, RunStartInput
from experiment_os.services.completion import CompletionContractService
from experiment_os.services.runs import RunRecorder


def test_completion_contract_accepts_direct_mcp_protocol_run(session):
    recorder = RunRecorder(session)
    run = recorder.start_run(
        RunStartInput(
            task="completion contract",
            metadata={"protocol": "experiment_os.pre_work.v1"},
        )
    )
    for event_type, payload in [
        ("brief_loaded", {"brief_id": "brief.test", "protocol": "experiment_os.pre_work.v1"}),
        (
            "dependency_resolved",
            {
                "dependency_pages": ["knowledge.python-api-drift-local-shim"],
                "protocol": "experiment_os.pre_work.v1",
            },
        ),
        ("test_run", {"command": "python -m pytest", "passed": True}),
        ("final_answer", {"summary": "done"}),
    ]:
        recorder.record_event(
            RunEventInput(
                run_id=run["run_id"],
                event_type=event_type,
                payload=payload,
            )
        )

    validation = CompletionContractService(session).validate(run["run_id"])

    assert validation["status"] == "passed"
    assert validation["violations"] == []


def test_completion_contract_reports_missing_required_steps(session):
    recorder = RunRecorder(session)
    run = recorder.start_run(RunStartInput(task="incomplete"))

    validation = CompletionContractService(session).validate(run["run_id"])

    assert validation["status"] == "failed"
    assert "pre_work_missing" in validation["violations"]
    assert "test_run_missing" in validation["violations"]
