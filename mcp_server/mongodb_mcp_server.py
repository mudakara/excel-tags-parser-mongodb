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
            name="get_available_fields",
            description="Get a list of ALL queryable fields in the database, including all dynamically extracted tag fields. This shows what fields you can filter, group, and aggregate by.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="advanced_query",
            description="Query resources using ANY combination of fields. Pass field names and values as a dictionary. Supports all dynamic fields like primaryContact, usage, department, costCenter, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Dictionary of field:value pairs to filter by (e.g., {'primaryContact': 'john', 'department': 'IT'})"
                    },
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 100)"},
                    "fields_to_return": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of fields to return in results (default: all fields)"
                    }
                },
                "required": ["filters"]
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
            name="aggregate_by_any_field",
            description="Count and aggregate documents grouped by ANY field in the database (supports all dynamic fields). Can also calculate sum/avg of numeric fields.",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_by_field": {
                        "type": "string",
                        "description": "Field to group by (e.g., 'primaryContact', 'department', 'usage', 'costCenter', etc.)"
                    },
                    "aggregation_type": {
                        "type": "string",
                        "enum": ["count", "sum", "avg"],
                        "description": "Type of aggregation: count (default), sum, or avg"
                    },
                    "value_field": {
                        "type": "string",
                        "description": "Field to sum/avg (required for sum/avg aggregation, e.g., 'cost')"
                    },
                    "limit": {"type": "integer", "description": "Maximum number of groups to return (default: 20)"},
                    "sort_order": {
                        "type": "string",
                        "enum": ["desc", "asc"],
                        "description": "Sort order: desc (default) or asc"
                    }
                },
                "required": ["group_by_field"]
            }
        ),
        Tool(
            name="cost_analysis_by_field",
            description="Analyze total cost grouped by any field (e.g., by department, primaryContact, usage, costCenter). Returns cost breakdown with sum, avg, min, max.",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_by_field": {
                        "type": "string",
                        "description": "Field to group costs by (e.g., 'department', 'primaryContact', 'usage')"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters to apply before grouping (e.g., {'environment': 'production'})"
                    },
                    "limit": {"type": "integer", "description": "Maximum number of groups to return (default: 20)"}
                },
                "required": ["group_by_field"]
            }
        ),
        Tool(
            name="multi_dimensional_analysis",
            description="Cross-tabulate two fields to see relationships (e.g., department vs environment, primaryContact vs applicationName). Creates a matrix showing counts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "field1": {
                        "type": "string",
                        "description": "First dimension field (rows)"
                    },
                    "field2": {
                        "type": "string",
                        "description": "Second dimension field (columns)"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters to apply (e.g., {'date': '2025-11'})"
                    },
                    "limit": {"type": "integer", "description": "Maximum number of items per dimension (default: 20)"}
                },
                "required": ["field1", "field2"]
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

        elif name == "get_available_fields":
            return await get_available_fields()

        elif name == "advanced_query":
            return await advanced_query(
                arguments.get("filters", {}),
                arguments.get("limit", 100),
                arguments.get("fields_to_return")
            )

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

        elif name == "aggregate_by_any_field":
            return await aggregate_by_any_field(
                arguments["group_by_field"],
                arguments.get("aggregation_type", "count"),
                arguments.get("value_field"),
                arguments.get("limit", 20),
                arguments.get("sort_order", "desc")
            )

        elif name == "cost_analysis_by_field":
            return await cost_analysis_by_field(
                arguments["group_by_field"],
                arguments.get("filters"),
                arguments.get("limit", 20)
            )

        elif name == "multi_dimensional_analysis":
            return await multi_dimensional_analysis(
                arguments["field1"],
                arguments["field2"],
                arguments.get("filters"),
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
    """Get database statistics (optimized to prevent context overflow)"""
    collection = get_collection()

    # Get counts only, not full distinct lists to prevent huge responses
    stats = {
        "total_documents": collection.count_documents({}),
        "unique_applications": len(collection.distinct("applicationName")),
        "unique_environments": len(collection.distinct("environment")),
        "unique_owners": len(collection.distinct("owner")),
        "date_range": {
            "earliest": collection.find_one({}, sort=[("date", 1)]).get("date") if collection.count_documents({}) > 0 else None,
            "latest": collection.find_one({}, sort=[("date", -1)]).get("date") if collection.count_documents({}) > 0 else None
        },
        "sample_environments": collection.distinct("environment")[:10],  # Only first 10 as samples
        "sample_applications": collection.distinct("applicationName")[:10],  # Only first 10 as samples
        "note": "Use get_available_fields for full field lists, or aggregate_by_any_field for detailed breakdowns"
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


async def get_available_fields() -> list[TextContent]:
    """Get all queryable fields in the database"""
    collection = get_collection()

    # Get a sample document to extract field names
    sample_doc = collection.find_one()

    if not sample_doc:
        return [TextContent(
            type="text",
            text=json.dumps({"message": "No documents found in database"}, indent=2)
        )]

    # Extract all top-level field names (excluding internal _id and nested objects)
    system_fields = ['_id', 'tags', 'originalData', 'metadata']

    all_fields = []
    dynamic_fields = []
    standard_fields = []

    for field in sample_doc.keys():
        if field not in system_fields:
            all_fields.append(field)
            # Categorize fields
            if field in ['applicationName', 'environment', 'owner', 'cost', 'date']:
                standard_fields.append(field)
            else:
                dynamic_fields.append(field)

    # Get unique values count for each field
    field_stats = {}
    for field in all_fields:
        try:
            unique_count = len(collection.distinct(field))
            non_null_count = collection.count_documents({field: {"$ne": None, "$exists": True}})
            field_stats[field] = {
                "unique_values": unique_count,
                "non_null_documents": non_null_count
            }
        except Exception as e:
            logger.warning(f"Error getting stats for field {field}: {e}")
            field_stats[field] = {"error": str(e)}

    result = {
        "total_fields": len(all_fields),
        "standard_fields": standard_fields,
        "dynamic_fields": dynamic_fields,
        "field_statistics": field_stats,
        "usage_examples": {
            "query_by_field": "Use advanced_query with filters={'fieldName': 'value'}",
            "aggregate_by_field": "Use aggregate_by_any_field with group_by_field='fieldName'",
            "cost_analysis": "Use cost_analysis_by_field with group_by_field='fieldName'"
        }
    }

    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def advanced_query(
    filters: dict,
    limit: int = 100,
    fields_to_return: list = None
) -> list[TextContent]:
    """
    Advanced query supporting ANY field combination.

    Args:
        filters: Dictionary of field:value pairs (e.g., {'primaryContact': 'john', 'department': 'IT'})
        limit: Maximum number of results
        fields_to_return: List of fields to include in results (None = all fields)
    """
    collection = get_collection()

    # Build projection if fields_to_return is specified
    projection = None
    if fields_to_return:
        projection = {field: 1 for field in fields_to_return}
        projection['_id'] = 0  # Exclude _id unless explicitly requested

    # Execute query
    if projection:
        results = list(collection.find(filters, projection).limit(limit))
    else:
        results = list(collection.find(filters).limit(limit))

    # Format response
    response = {
        "filters_applied": filters,
        "count": len(results),
        "limit": limit,
        "results": results
    }

    return [TextContent(
        type="text",
        text=json.dumps(response, indent=2, default=str)
    )]


async def aggregate_by_any_field(
    group_by_field: str,
    aggregation_type: str = "count",
    value_field: str = None,
    limit: int = 20,
    sort_order: str = "desc"
) -> list[TextContent]:
    """
    Aggregate documents by ANY field with flexible aggregation types.

    Args:
        group_by_field: Field to group by (can be any field in the database)
        aggregation_type: Type of aggregation - count, sum, or avg
        value_field: Field to sum/avg (required for sum/avg)
        limit: Maximum number of groups to return
        sort_order: Sort order (desc or asc)
    """
    collection = get_collection()

    # Build aggregation pipeline
    pipeline = []

    # Group stage
    if aggregation_type == "count":
        pipeline.append({
            "$group": {
                "_id": f"${group_by_field}",
                "value": {"$sum": 1}
            }
        })
        value_label = "count"

    elif aggregation_type == "sum":
        if not value_field:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "value_field is required for sum aggregation"}, indent=2)
            )]
        pipeline.append({
            "$group": {
                "_id": f"${group_by_field}",
                "value": {"$sum": f"${value_field}"},
                "count": {"$sum": 1}
            }
        })
        value_label = f"sum_of_{value_field}"

    elif aggregation_type == "avg":
        if not value_field:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "value_field is required for avg aggregation"}, indent=2)
            )]
        pipeline.append({
            "$group": {
                "_id": f"${group_by_field}",
                "value": {"$avg": f"${value_field}"},
                "count": {"$sum": 1}
            }
        })
        value_label = f"avg_of_{value_field}"

    # Sort stage
    sort_direction = -1 if sort_order == "desc" else 1
    pipeline.append({"$sort": {"value": sort_direction}})

    # Limit stage
    pipeline.append({"$limit": limit})

    try:
        results = list(collection.aggregate(pipeline))

        # Format results
        formatted_results = []
        for r in results:
            result_item = {
                group_by_field: r["_id"] or "Unknown",
                value_label: r["value"]
            }
            if "count" in r:
                result_item["count"] = r["count"]
            formatted_results.append(result_item)

        response = {
            "group_by_field": group_by_field,
            "aggregation_type": aggregation_type,
            "value_field": value_field if value_field else "N/A",
            "results": formatted_results,
            "total_groups": len(results)
        }

        return [TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in aggregate_by_any_field: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def cost_analysis_by_field(
    group_by_field: str,
    filters: dict = None,
    limit: int = 20
) -> list[TextContent]:
    """
    Analyze costs grouped by any field.

    Args:
        group_by_field: Field to group costs by (e.g., 'department', 'primaryContact', 'usage')
        filters: Optional filters to apply before grouping
        limit: Maximum number of groups to return
    """
    collection = get_collection()

    # Build aggregation pipeline
    pipeline = []

    # Match stage (if filters provided)
    if filters:
        pipeline.append({"$match": filters})

    # Add numeric cost field
    pipeline.append({
        "$addFields": {
            "numericCost": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$cost"}, "string"]},
                    "then": {"$toDouble": {"$ifNull": ["$cost", "0"]}},
                    "else": {"$ifNull": ["$cost", 0]}
                }
            }
        }
    })

    # Group stage
    pipeline.append({
        "$group": {
            "_id": f"${group_by_field}",
            "totalCost": {"$sum": "$numericCost"},
            "avgCost": {"$avg": "$numericCost"},
            "minCost": {"$min": "$numericCost"},
            "maxCost": {"$max": "$numericCost"},
            "count": {"$sum": 1}
        }
    })

    # Sort by total cost (descending)
    pipeline.append({"$sort": {"totalCost": -1}})

    # Limit
    pipeline.append({"$limit": limit})

    try:
        results = list(collection.aggregate(pipeline))

        # Calculate grand total
        grand_total = sum(r["totalCost"] for r in results)

        # Format results
        formatted_results = []
        for r in results:
            percentage = (r["totalCost"] / grand_total * 100) if grand_total > 0 else 0
            formatted_results.append({
                group_by_field: r["_id"] or "Unknown",
                "totalCost": round(r["totalCost"], 2),
                "avgCost": round(r["avgCost"], 2),
                "minCost": round(r["minCost"], 2),
                "maxCost": round(r["maxCost"], 2),
                "resourceCount": r["count"],
                "percentageOfTotal": round(percentage, 2)
            })

        response = {
            "group_by_field": group_by_field,
            "filters_applied": filters if filters else {},
            "grand_total_cost": round(grand_total, 2),
            "results": formatted_results,
            "total_groups": len(results)
        }

        return [TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in cost_analysis_by_field: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def multi_dimensional_analysis(
    field1: str,
    field2: str,
    filters: dict = None,
    limit: int = 20
) -> list[TextContent]:
    """
    Cross-tabulate two fields to analyze relationships.

    Args:
        field1: First dimension (rows)
        field2: Second dimension (columns)
        filters: Optional filters to apply
        limit: Maximum number of items per dimension
    """
    collection = get_collection()

    # Build aggregation pipeline
    pipeline = []

    # Match stage (if filters provided)
    if filters:
        pipeline.append({"$match": filters})

    # Group by both fields
    pipeline.append({
        "$group": {
            "_id": {
                "field1": f"${field1}",
                "field2": f"${field2}"
            },
            "count": {"$sum": 1}
        }
    })

    try:
        results = list(collection.aggregate(pipeline))

        # Convert to matrix format
        matrix = {}
        field1_values = set()
        field2_values = set()

        for r in results:
            f1_val = r["_id"]["field1"] or "Unknown"
            f2_val = r["_id"]["field2"] or "Unknown"
            count = r["count"]

            field1_values.add(f1_val)
            field2_values.add(f2_val)

            if f1_val not in matrix:
                matrix[f1_val] = {}
            matrix[f1_val][f2_val] = count

        # Limit dimensions if needed
        field1_values = sorted(list(field1_values))[:limit]
        field2_values = sorted(list(field2_values))[:limit]

        # Build formatted matrix
        formatted_matrix = []
        for f1_val in field1_values:
            row = {field1: f1_val}
            for f2_val in field2_values:
                row[f2_val] = matrix.get(f1_val, {}).get(f2_val, 0)
            formatted_matrix.append(row)

        response = {
            "field1": field1,
            "field2": field2,
            "field1_values": field1_values,
            "field2_values": field2_values,
            "filters_applied": filters if filters else {},
            "matrix": formatted_matrix,
            "total_combinations": len(results)
        }

        return [TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in multi_dimensional_analysis: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
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
