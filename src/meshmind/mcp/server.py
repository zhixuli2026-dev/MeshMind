"""MCP Server — exposes MeshMind as tools for external multi-agent systems."""

import json
from uuid import UUID

from mcp.server import Server
from mcp.types import Tool, TextContent

from meshmind.api.deps import get_harness, get_storage
from meshmind.core.extraction import ExtractionPipeline
from meshmind.core.graph import KnowledgeGraph
from meshmind.core.retrieval import KnowledgeRetrieval
from meshmind.db.engine import AsyncSessionFactory


def create_mcp_server() -> Server:
    server = Server("meshmind")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="search_knowledge", description="Search team knowledge", inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "workspace_id": {"type": "string", "description": "Workspace UUID"},
                },
                "required": ["query", "workspace_id"],
            }),
            Tool(name="get_knowledge", description="Get a single knowledge node", inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string"},
                    "workspace_id": {"type": "string"},
                },
                "required": ["node_id", "workspace_id"],
            }),
            Tool(name="list_related", description="Get related knowledge nodes", inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string"},
                    "workspace_id": {"type": "string"},
                },
                "required": ["node_id", "workspace_id"],
            }),
            Tool(name="extract_knowledge", description="Extract knowledge from conversation", inputSchema={
                "type": "object",
                "properties": {
                    "messages": {"type": "array", "items": {"type": "object"}},
                    "workspace_id": {"type": "string"},
                    "user_id": {"type": "string"},
                    "session_id": {"type": "string"},
                },
                "required": ["messages", "workspace_id", "user_id", "session_id"],
            }),
            Tool(name="add_document", description="Upload document and extract knowledge", inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "title": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "user_id": {"type": "string"},
                },
                "required": ["content", "title", "workspace_id", "user_id"],
            }),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        ws_id = UUID(arguments["workspace_id"])

        if name == "search_knowledge":
            async with AsyncSessionFactory() as session:
                retrieval = KnowledgeRetrieval(session, ws_id)
                encoder = server.app.state.encoder if hasattr(server, "app") else None
                embedding = encoder.encode_single(arguments["query"]) if encoder else None
                results = await retrieval.hybrid_search(arguments["query"], embedding=embedding)
                return [TextContent(type="text", text=json.dumps(results, ensure_ascii=False))]

        elif name == "get_knowledge":
            async with AsyncSessionFactory() as session:
                graph = KnowledgeGraph(session, ws_id)
                node = await graph.get_node(UUID(arguments["node_id"]))
                return [TextContent(type="text", text=json.dumps(node, ensure_ascii=False))]

        elif name == "list_related":
            async with AsyncSessionFactory() as session:
                retrieval = KnowledgeRetrieval(session, ws_id)
                related = await retrieval.get_related_nodes(UUID(arguments["node_id"]))
                return [TextContent(type="text", text=json.dumps(related, ensure_ascii=False))]

        elif name == "extract_knowledge":
            harness = get_harness()
            encoder = server.app.state.encoder if hasattr(server, "app") else None
            async with AsyncSessionFactory() as session:
                graph = KnowledgeGraph(session, ws_id)
                pipeline = ExtractionPipeline(harness, encoder, get_storage())
                result = await pipeline.extract_from_conversation(
                    messages=arguments["messages"],
                    graph=graph,
                    user_id=arguments["user_id"],
                    session_id=arguments["session_id"],
                )
                await session.commit()
                return [TextContent(type="text", text=json.dumps({
                    "status": result.status, "created_nodes": result.created_nodes,
                }, ensure_ascii=False))]

        elif name == "add_document":
            harness = get_harness()
            encoder = server.app.state.encoder if hasattr(server, "app") else None
            async with AsyncSessionFactory() as session:
                graph = KnowledgeGraph(session, ws_id)
                pipeline = ExtractionPipeline(harness, encoder, get_storage())
                result = await pipeline.extract_from_document(
                    content=arguments["content"],
                    title=arguments["title"],
                    graph=graph,
                    user_id=arguments["user_id"],
                )
                await session.commit()
                return [TextContent(type="text", text=json.dumps({
                    "status": result.status, "created_nodes": result.created_nodes,
                }, ensure_ascii=False))]

        return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}))]

    return server
