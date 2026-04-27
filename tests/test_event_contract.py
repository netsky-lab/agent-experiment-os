from experiment_os.services.event_contract import AgentEventContract, event_contract_prompt


def test_event_contract_lists_pre_edit_required_events():
    contract = AgentEventContract().as_dict()

    assert contract["version"] == "experiment_os.agent_events.v1"
    assert "package_version_checked" in contract["required_before_first_edit"]
    assert "file_inspected" in contract["required_before_first_edit"]
    assert "record_run_event" in event_contract_prompt()
