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

