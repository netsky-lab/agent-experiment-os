from experiment_os.services.codex_events import CodexJsonlEventExtractor


def test_codex_jsonl_extractor_reads_structured_events():
    jsonl = """
{"type":"exec_command.begin","cmd":"cat package.json && rg migration drizzle/migrations"}
{"type":"agent_message","message":"drizzle-orm@1.0.0-beta.22"}
{"type":"exec_command.end","cmd":"npm run db:generate","output":"passed","exit_code":0}
{"type":"file_change","summary":"modified src/db/schema.ts"}
{"type":"error","message":"tool call failed after retry"}
"""

    events = CodexJsonlEventExtractor().extract(run_id="run.test", jsonl=jsonl)
    event_types = [event.event_type for event in events]

    assert "package_version_checked" in event_types
    assert "file_inspected" in event_types
    assert "file_edited" in event_types
    assert "test_run" in event_types
    assert any(event.payload.get("failure_type") == "tool_call_failure" for event in events)
