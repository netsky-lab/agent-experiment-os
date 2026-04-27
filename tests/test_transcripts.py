from experiment_os.services.transcripts import TranscriptEventExtractor


def test_transcript_extractor_finds_versions_inspection_edits_and_tests():
    transcript = """
cat package.json
drizzle-orm@1.0.0-beta.22
rg migration drizzle/migrations
modified src/db/schema.ts
npm run db:generate passed
"""

    events = TranscriptEventExtractor().extract(run_id="run.test", transcript=transcript)
    event_types = [event.event_type for event in events]

    assert "package_version_checked" in event_types
    assert "file_inspected" in event_types
    assert "file_edited" in event_types
    assert "test_run" in event_types


def test_transcript_extractor_parses_opencode_json_without_prompt_false_edits():
    transcript = """$ opencode run --format json '# Context
Do not edit tests/test_client.py or agent_client/vendor_sdk.py'
{"type":"tool_use","part":{"type":"tool","tool":"read","state":{"status":"completed","input":{"filePath":"/repo/agent_client/vendor_sdk.py"}}}}
{"type":"tool_use","part":{"type":"tool","tool":"edit","state":{"status":"completed","input":{"filePath":"/repo/agent_client/client.py"}}}}
{"type":"tool_use","part":{"type":"tool","tool":"bash","state":{"status":"completed","input":{"command":"python -m pytest"},"metadata":{"exit":0}}}}
{"type":"text","part":{"type":"text","text":"Tests pass."}}
"""

    events = TranscriptEventExtractor().extract(run_id="run.test", transcript=transcript)
    edited_paths = [
        event.payload["path"] for event in events if event.event_type == "file_edited"
    ]
    event_types = [event.event_type for event in events]

    assert edited_paths == ["/repo/agent_client/client.py"]
    assert "file_inspected" in event_types
    assert "test_run" in event_types
    assert "final_answer" in event_types
