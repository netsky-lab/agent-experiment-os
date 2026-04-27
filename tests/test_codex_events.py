from experiment_os.services.codex_events import CodexJsonlEventExtractor


def test_codex_jsonl_extractor_reads_structured_events():
    jsonl = "\n".join(
        [
            (
                '{"type":"exec_command.begin",'
                '"cmd":"cat package.json && rg migration drizzle/migrations"}'
            ),
            '{"type":"agent_message","message":"drizzle-orm@1.0.0-beta.22"}',
            (
                '{"type":"exec_command.end","cmd":"npm run db:generate",'
                '"output":"passed","exit_code":0}'
            ),
            '{"type":"file_change","summary":"modified src/db/schema.ts"}',
            (
                '{"type":"item.completed","item":{"type":"file_change",'
                '"changes":[{"path":"/tmp/repo/package.json","kind":"update"}]}}'
            ),
            (
                '{"type":"item.completed","item":{"type":"mcp_tool_call",'
                '"server":"experiment_os","tool":"start_pre_work_protocol",'
                '"arguments":{},"status":"completed"}}'
            ),
            (
                '{"type":"item.completed","item":{"type":"mcp_tool_call",'
                '"server":"experiment_os","tool":"record_run_event",'
                '"arguments":{"run_id":"run.inner","event_type":"final_answer"},'
                '"status":"completed"}}'
            ),
            '{"type":"error","message":"tool call failed after retry"}',
        ]
    )

    events = CodexJsonlEventExtractor().extract(run_id="run.test", jsonl=jsonl)
    event_types = [event.event_type for event in events]

    assert "package_version_checked" in event_types
    assert "file_inspected" in event_types
    assert "file_edited" in event_types
    assert "test_run" in event_types
    assert any(event.payload.get("path") == "/tmp/repo/package.json" for event in events)
    assert any(event.payload.get("failure_type") == "tool_call_failure" for event in events)
    assert any(event.event_type == "mcp_tool_called" for event in events)
    assert any(event.payload.get("recorded_event_type") == "final_answer" for event in events)
