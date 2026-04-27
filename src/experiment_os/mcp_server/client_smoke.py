import json
import os
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import TextContent


async def run_mcp_smoke() -> dict[str, Any]:
    params = StdioServerParameters(
        command="uv",
        args=["run", "experiment-os", "mcp", "serve"],
        env={**os.environ},
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            protocol = await _call_json(
                session,
                "start_pre_work_protocol",
                {
                    "task": "Fix a Drizzle migration issue in a Python CLI repo",
                    "repo": "example/repo",
                    "libraries": ["drizzle"],
                    "agent": "opencode",
                    "model": "gemma",
                    "toolchain": "shell",
                },
            )
            brief = protocol["brief"]
            dependencies = protocol["dependencies"]
            run = protocol["run"]
            agent_graph = protocol["agent_dependency_graph"]
            dependencies = await _call_json(
                session,
                "resolve_dependencies",
                {"page_ids": brief["required_pages"], "depth": 2},
            )
            event = await _call_json(
                session,
                "record_run_event",
                {
                    "run_id": run["run_id"],
                    "event_type": "brief_loaded",
                    "payload": {
                        "brief_id": brief["brief_id"],
                        "required_pages": brief["required_pages"],
                    },
                },
            )
            search = await _call_json(
                session,
                "search_issue_knowledge",
                {
                    "library": "drizzle",
                    "topic": "migration default",
                    "limit": 5,
                },
            )

    return {
        "brief_id": brief["brief_id"],
        "required_pages": brief["required_pages"],
        "agent_graph_load_order": agent_graph["load_order"],
        "dependency_pages": [page["id"] for page in dependencies["pages"]],
        "run_id": run["run_id"],
        "event_id": event["event_id"],
        "issue_results": [result["id"] for result in search["results"]],
    }


async def _call_json(
    session: ClientSession,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    result = await session.call_tool(tool_name, arguments)
    if result.isError:
        raise RuntimeError(f"MCP tool failed: {tool_name}: {result.content}")

    for content in result.content:
        if isinstance(content, TextContent):
            return json.loads(content.text)

    raise RuntimeError(f"MCP tool returned no text content: {tool_name}")
