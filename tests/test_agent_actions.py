from experiment_os.domain.schemas import RunEventInput, RunStartInput
from experiment_os.services.agent_actions import AgentActionService
from experiment_os.services.runs import RunRecorder


def test_agent_action_service_walks_strict_protocol(session):
    recorder = RunRecorder(session)
    run = recorder.start_run(RunStartInput(task="strict protocol"))
    run_id = run["run_id"]

    first = AgentActionService(session).next_required_action(run_id)
    assert first["next_action"]["id"] == "start_pre_work_protocol"

    for event_type, payload in [
        ("brief_loaded", {"brief_id": "brief.test", "protocol": "experiment_os.pre_work.v1"}),
        ("dependency_resolved", {"dependency_pages": ["policy.test"], "protocol": "experiment_os.pre_work.v1"}),
    ]:
        recorder.record_event(RunEventInput(run_id=run_id, event_type=event_type, payload=payload))

    before_edit = AgentActionService(session).next_required_action(run_id)
    assert before_edit["next_action"]["id"] == "record_decision"

    for event_type, payload in [
        ("decision_recorded", {"decision": "minimal patch", "evidence_ids": ["policy.test"]}),
        ("file_edited", {"paths": ["src/app.py"]}),
        ("test_run", {"command": "pytest", "passed": True}),
    ]:
        recorder.record_event(RunEventInput(run_id=run_id, event_type=event_type, payload=payload))

    final = AgentActionService(session).next_required_action(run_id)
    assert final["next_action"]["id"] == "complete_run"
