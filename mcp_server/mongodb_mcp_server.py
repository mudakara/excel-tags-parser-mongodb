#!/usr/bin/env python3
"""
MongoDB MCP Server for Azure Resources Analytics

This MCP server provides tools for querying MongoDB and generating charts/reports
for Azure resources data. It can be used with open-source LLMs.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
from datetime import datetime

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mongodb-mcp-server")

# MongoDB Configuration
MONGODB_URI = "mongodb://localhost:27017/"
MONGODB_DATABASE = "azure"
MONGODB_COLLECTION = "resources"

# Initialize MCP server
app = Server("mongodb-azure-analytics")

# MongoDB client (initialized when needed)
_mongodb_client = None


def get_mongodb_client():
    """Get MongoDB client instance"""
    global _mongodb_client
    if _mongodb_client is None:
        _mongodb_client = MongoClient(MONGODB_URI)
    return _mongodb_client


def get_collection():
    """Get MongoDB collection"""
    client = get_mongodb_client()
    db = client[MONGODB_DATABASE]
    return db[MONGODB_COLLECTION]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for the LLM"""
    return [
        Tool(
            name="get_database_schema",
            description="Get the schema and structure of the MongoDB database, including sample documents",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="query_resources",
            description="Query Azure resources with filters. Returns matching documents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "applicationName": {"type": "string", "description": "Filter by application name"},
                    "environment": {"type": "string", "description": "Filter by environment (e.g., production, dev)"},
                    "owner": {"type": "string", "description": "Filter by owner"},
                    "cost": {"type": "string", "description": "Filter by cost"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 100)"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_statistics",
            description="Get overall statistics about the database (total docs, unique apps, environments, owners)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="aggregate_by_field",
            description="Count documents grouped by a specific field (applicationName, environment, owner, or cost)",
            inputSchema={
                "type": "object",
                "properties": {
                    "field": {
                        "type": "string",
                        "enum": ["applicationName", "environment", "owner", "cost"],
                        "description": "Field to group by"
                    },
                    "limit": {"type": "integer", "description": "Maximum number of groups to return (default: 20)"}
                },
                "required": ["field"]
            }
        ),
        Tool(
            name="create_bar_chart",
            description="Create a bar chart showing distribution of resources by a field",
            inputSchema={
                "type": "object",
                "properties": {
                    "field": {
                        "type": "string",
                        "enum": ["applicationName", "environment", "owner", "cost"],
                        "description": "Field to create chart for"
                    },
                    "title": {"type": "string", "description": "Chart title"},
                    "limit": {"type": "integer", "description": "Number of top items to show (default: 15)"}
                },
                "required": ["field"]
            }
        ),
        Tool(
            name="create_pie_chart",
            description="Create a pie chart showing distribution of resources",
            inputSchema={
                "type": "object",
                "properties": {
                    "field": {
                        "type": "string",
                        "enum": ["applicationName", "environment", "owner", "cost"],
                        "description": "Field to create pie chart for"
                    },
                    "title": {"type": "string", "description": "Chart title"},
                    "limit": {"type": "integer", "description": "Number of top items to show (default: 10)"}
                },
                "required": ["field"]
            }
        ),
        Tool(
            name="create_environment_app_matrix",
            description="Create a heatmap showing application distribution across environments",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Chart title"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_resources_by_owner",
            description="Get detailed breakdown of resources owned by each owner",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of owners to show (default: 10)"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_total_cost",
            description="Calculate total cost with optional filters for environment, application name, owner, and date. Returns sum of all costs matching the filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "applicationName": {"type": "string", "description": "Filter by application name"},
                    "environment": {"type": "string", "description": "Filter by environment (e.g., production, dev, test)"},
                    "owner": {"type": "string", "description": "Filter by owner"},
                    "date": {"type": "string", "description": "Filter by date in YYYY-MM format (e.g., 2024-01, 2025-11)"}
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls from the LLM"""

    try:
        if name == "get_database_schema":
            return await get_database_schema()

        elif name == "query_resources":
            return await query_resources(
                arguments.get("applicationName"),
                arguments.get("environment"),
                arguments.get("owner"),
                arguments.get("cost"),
                arguments.get("limit", 100)
            )

        elif name == "get_statistics":
            return await get_statistics()

        elif name == "aggregate_by_field":
            return await aggregate_by_field(
                arguments["field"],
                arguments.get("limit", 20)
            )

        elif name == "create_bar_chart":
            return await create_bar_chart(
                arguments["field"],
                arguments.get("title"),
                arguments.get("limit", 15)
            )

        elif name == "create_pie_chart":
            return await create_pie_chart(
                arguments["field"],
                arguments.get("title"),
                arguments.get("limit", 10)
            )

        elif name == "create_environment_app_matrix":
            return await create_environment_app_matrix(
                arguments.get("title")
            )

        elif name == "get_resources_by_owner":
            return await get_resources_by_owner(
                arguments.get("limit", 10)
            )

        elif name == "get_total_cost":
            return await get_total_cost(
                arguments.get("applicationName"),
                arguments.get("environment"),
                arguments.get("owner"),
                arguments.get("date")
            )

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        logger.error(f"Error in {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def get_database_schema() -> list[TextContent]:
    """Get database schema information"""
    collection = get_collection()

    # Get sample document
    sample_doc = collection.find_one()

    # Get collection stats
    stats = {
        "total_documents": collection.count_documents({}),
        "database": MONGODB_DATABASE,
        "collection": MONGODB_COLLECTION
    }

    # Format schema info
    schema_info = {
        "database_stats": stats,
        "document_structure": {
            "applicationName": "Top-level field for filtering/grouping applications",
            "environment": "Top-level field for filtering/grouping environments",
            "owner": "Top-level field for filtering/grouping owners",
            "cost": "Top-level field for cost values (numeric or string)",
            "date": "Top-level field for date in YYYY-MM format (e.g., 2024-01, 2025-11)",
            "tags": {
                "raw": "Original tag string from Excel",
                "parsed": "Parsed tag values (applicationName, environment, owner)"
            },
            "originalData": "All original Excel columns preserved here",
            "metadata": {
                "importDate": "When data was imported (ISO format)",
                "sourceFile": "Original Excel filename",
                "dataDate": "Date from Summary sheet (YYYY-MM format)"
            }
        },
        "sample_document": sample_doc if sample_doc else "No documents found"
    }

    return [TextContent(
        type="text",
        text=json.dumps(schema_info, indent=2, default=str)
    )]


async def query_resources(
    application_name: str = None,
    environment: str = None,
    owner: str = None,
    cost: str = None,
    limit: int = 100
) -> list[TextContent]:
    """Query resources with filters"""
    collection = get_collection()

    # Build query
    query = {}
    if application_name:
        query["applicationName"] = application_name
    if environment:
        query["environment"] = environment
    if owner:
        query["owner"] = owner
    if cost:
        query["cost"] = cost

    # Execute query
    results = list(collection.find(query).limit(limit))

    # Format results
    response = {
        "query": query,
        "count": len(results),
        "results": results
    }

    return [TextContent(
        type="text",
        text=json.dumps(response, indent=2, default=str)
    )]


async def get_statistics() -> list[TextContent]:
    """Get database statistics"""
    collection = get_collection()

    stats = {
        "total_documents": collection.count_documents({}),
        "unique_applications": len(collection.distinct("applicationName")),
        "unique_environments": len(collection.distinct("environment")),
        "unique_owners": len(collection.distinct("owner")),
        "unique_costs": len(collection.distinct("cost")),
        "applications": collection.distinct("applicationName"),
        "environments": collection.distinct("environment"),
        "owners": collection.distinct("owner"),
        "costs": collection.distinct("cost")
    }

    return [TextContent(
        type="text",
        text=json.dumps(stats, indent=2, default=str)
    )]


async def aggregate_by_field(field: str, limit: int = 20) -> list[TextContent]:
    """Aggregate documents by field"""
    collection = get_collection()

    pipeline = [
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]

    results = list(collection.aggregate(pipeline))

    # Format results
    formatted_results = [
        {field: r["_id"], "count": r["count"]}
        for r in results
    ]

    return [TextContent(
        type="text",
        text=json.dumps({
            "field": field,
            "results": formatted_results,
            "total_groups": len(results)
        }, indent=2)
    )]


async def create_bar_chart(field: str, title: str = None, limit: int = 15) -> list[ImageContent]:
    """Create a bar chart"""
    collection = get_collection()

    # Get aggregated data
    pipeline = [
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]

    results = list(collection.aggregate(pipeline))

    # Create DataFrame
    df = pd.DataFrame([
        {field: r["_id"] or "Unknown", "count": r["count"]}
        for r in results
    ])

    # Create bar chart
    if title is None:
        title = f"Resources by {field.replace('Name', ' Name')}"

    fig = px.bar(
        df,
        x=field,
        y="count",
        title=title,
        labels={field: field.replace("Name", " Name"), "count": "Number of Resources"},
        color="count",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False
    )

    # Convert to PNG
    img_bytes = pio.to_image(fig, format="png")
    import base64
    img_base64 = base64.b64encode(img_bytes).decode()

    return [ImageContent(
        type="image",
        data=img_base64,
        mimeType="image/png"
    )]


async def create_pie_chart(field: str, title: str = None, limit: int = 10) -> list[ImageContent]:
    """Create a pie chart"""
    collection = get_collection()

    # Get aggregated data
    pipeline = [
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]

    results = list(collection.aggregate(pipeline))

    # Create DataFrame
    df = pd.DataFrame([
        {field: r["_id"] or "Unknown", "count": r["count"]}
        for r in results
    ])

    # Create pie chart
    if title is None:
        title = f"Distribution by {field.replace('Name', ' Name')}"

    fig = px.pie(
        df,
        values="count",
        names=field,
        title=title
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)

    # Convert to PNG
    img_bytes = pio.to_image(fig, format="png")
    import base64
    img_base64 = base64.b64encode(img_bytes).decode()

    return [ImageContent(
        type="image",
        data=img_base64,
        mimeType="image/png"
    )]


async def create_environment_app_matrix(title: str = None) -> list[ImageContent]:
    """Create a heatmap of applications across environments"""
    collection = get_collection()

    # Get data
    pipeline = [
        {"$group": {
            "_id": {
                "app": "$applicationName",
                "env": "$environment"
            },
            "count": {"$sum": 1}
        }}
    ]

    results = list(collection.aggregate(pipeline))

    # Create DataFrame
    data = []
    for r in results:
        if r["_id"]["app"] and r["_id"]["env"]:
            data.append({
                "Application": r["_id"]["app"],
                "Environment": r["_id"]["env"],
                "Count": r["count"]
            })

    df = pd.DataFrame(data)

    if df.empty:
        return [TextContent(type="text", text="No data available for heatmap")]

    # Pivot for heatmap
    pivot_df = df.pivot_table(
        values="Count",
        index="Application",
        columns="Environment",
        fill_value=0
    )

    # Create heatmap
    if title is None:
        title = "Application Distribution Across Environments"

    fig = px.imshow(
        pivot_df,
        labels=dict(x="Environment", y="Application", color="Count"),
        title=title,
        color_continuous_scale="YlOrRd"
    )

    fig.update_layout(height=max(500, len(pivot_df) * 20))

    # Convert to PNG
    img_bytes = pio.to_image(fig, format="png")
    import base64
    img_base64 = base64.b64encode(img_bytes).decode()

    return [ImageContent(
        type="image",
        data=img_base64,
        mimeType="image/png"
    )]


async def get_resources_by_owner(limit: int = 10) -> list[TextContent]:
    """Get resources breakdown by owner"""
    collection = get_collection()

    pipeline = [
        {"$group": {
            "_id": "$owner",
            "count": {"$sum": 1},
            "applications": {"$addToSet": "$applicationName"},
            "environments": {"$addToSet": "$environment"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]

    results = list(collection.aggregate(pipeline))

    # Format results
    owner_breakdown = []
    for r in results:
        owner_breakdown.append({
            "owner": r["_id"] or "Unknown",
            "total_resources": r["count"],
            "unique_applications": len([a for a in r["applications"] if a]),
            "unique_environments": len([e for e in r["environments"] if e]),
            "applications": [a for a in r["applications"] if a],
            "environments": [e for e in r["environments"] if e]
        })

    return [TextContent(
        type="text",
        text=json.dumps({
            "owner_breakdown": owner_breakdown,
            "total_owners": len(results)
        }, indent=2)
    )]


async def get_total_cost(
    application_name: str = None,
    environment: str = None,
    owner: str = None,
    date: str = None
) -> list[TextContent]:
    """
    Calculate total cost with optional filters for environment, application name, owner, and date.

    Uses MongoDB aggregation pipeline to sum all cost values matching the filters.
    Handles both numeric and string cost values by attempting to convert them.

    Args:
        application_name: Filter by application name
        environment: Filter by environment (e.g., production, dev, test)
        owner: Filter by owner
        date: Filter by date in YYYY-MM format (e.g., 2024-01, 2025-11)
    """
    collection = get_collection()

    # Build match stage based on filters
    match_stage = {}
    if application_name:
        match_stage["applicationName"] = application_name
    if environment:
        match_stage["environment"] = environment
    if owner:
        match_stage["owner"] = owner
    if date:
        match_stage["date"] = date

    # Build aggregation pipeline
    pipeline = []

    # Add match stage if there are filters
    if match_stage:
        pipeline.append({"$match": match_stage})

    # Add stage to convert cost to numeric and sum
    pipeline.extend([
        {
            "$addFields": {
                "numericCost": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$cost"}, "string"]},
                        "then": {"$toDouble": {"$ifNull": ["$cost", "0"]}},
                        "else": {"$ifNull": ["$cost", 0]}
                    }
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "totalCost": {"$sum": "$numericCost"},
                "count": {"$sum": 1},
                "avgCost": {"$avg": "$numericCost"},
                "minCost": {"$min": "$numericCost"},
                "maxCost": {"$max": "$numericCost"}
            }
        }
    ])

    try:
        results = list(collection.aggregate(pipeline))

        if results:
            result = results[0]
            response = {
                "filters": {
                    "applicationName": application_name,
                    "environment": environment,
                    "owner": owner,
                    "date": date
                },
                "totalCost": result.get("totalCost", 0),
                "resourceCount": result.get("count", 0),
                "averageCost": result.get("avgCost", 0),
                "minCost": result.get("minCost", 0),
                "maxCost": result.get("maxCost", 0)
            }
        else:
            response = {
                "filters": {
                    "applicationName": application_name,
                    "environment": environment,
                    "owner": owner,
                    "date": date
                },
                "totalCost": 0,
                "resourceCount": 0,
                "averageCost": 0,
                "minCost": 0,
                "maxCost": 0,
                "message": "No resources found matching the filters"
            }

        return [TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error calculating total cost: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "filters": {
                    "applicationName": application_name,
                    "environment": environment,
                    "owner": owner,
                    "date": date
                }
            }, indent=2)
        )]


async def main():
    """Main entry point for the MCP server"""
    from mcp.server.stdio import stdio_server

    logger.info("Starting MongoDB MCP Server for Azure Analytics")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
