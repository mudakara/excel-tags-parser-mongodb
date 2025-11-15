#!/usr/bin/env python3
"""
Test script to verify MCP server functionality
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from mongodb_mcp_server import (
    get_database_schema,
    get_statistics,
    query_resources,
    aggregate_by_field
)


async def main():
    """Run tests"""
    print("Testing MongoDB MCP Server...\n")

    try:
        # Test 1: Get database schema
        print("1. Testing get_database_schema...")
        schema = await get_database_schema()
        print(f"✅ Schema retrieved: {len(schema[0].text[:100])}... characters")
        print()

        # Test 2: Get statistics
        print("2. Testing get_statistics...")
        stats = await get_statistics()
        print(f"✅ Statistics retrieved")
        print(stats[0].text[:200])
        print()

        # Test 3: Query resources (limit 5)
        print("3. Testing query_resources...")
        results = await query_resources(limit=5)
        print(f"✅ Query executed")
        print()

        # Test 4: Aggregate by environment
        print("4. Testing aggregate_by_field (environment)...")
        agg = await aggregate_by_field("environment", limit=5)
        print(f"✅ Aggregation completed")
        print(agg[0].text[:200])
        print()

        print("\n🎉 All tests passed! MCP server is working correctly.")
        print("\nYou can now connect this server to an LLM.")
        print(f"\nServer path: {os.path.abspath(__file__).replace('test_mcp.py', 'mongodb_mcp_server.py')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure MongoDB is running: brew services start mongodb-community")
        print("2. Verify data exists in database: mongosh azure --eval 'db.resources.count()'")
        print("3. Check requirements: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
