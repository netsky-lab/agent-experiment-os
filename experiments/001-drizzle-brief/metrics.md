# Metrics

## Outcome Metrics

| Metric | Type | Notes |
| --- | --- | --- |
| task_success | boolean | Human or test-harness judged. |
| patch_correctness | enum | `correct`, `partial`, `incorrect`, `unsafe`. |
| tests_passing | boolean | Relevant tests or migration generation pass. |
| stale_api_usage_count | integer | Count of outdated Drizzle API assumptions. |
| unnecessary_file_edits | integer | Files changed outside expected scope. |

## Behavioral Metrics

| Metric | Type | Notes |
| --- | --- | --- |
| inspected_package_versions_before_edit | boolean | Key signal for issue-informed behavior. |
| inspected_migration_conventions_before_edit | boolean | Key signal for project-aware behavior. |
| time_to_first_relevant_file_inspection | duration | Lower is generally better. |
| retries_to_valid_patch | integer | Recovery efficiency. |
| over_repair_count | integer | Broad rewrites after narrow failure. |

## System Metrics

| Metric | Type | Notes |
| --- | --- | --- |
| brief_required_page_count | integer | Context size pressure. |
| brief_dependency_page_count | integer | Dependency expansion pressure. |
| brief_token_estimate | integer | Approximate budget usage. |
| issue_source_precision | float | Relevant issue sources / returned issue sources. |
| human_review_minutes | float | Review cost for issue-derived cards. |

