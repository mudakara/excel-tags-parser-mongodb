# MCP Tools Quick Start Guide

## 🚀 Getting Started

This guide shows you how to use the MongoDB MCP tools to query and analyze your data.

## 📋 Prerequisites

1. MongoDB running on `localhost:27017`
2. Data imported into the `azure.resources` collection
3. MCP server running (see installation below)

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
cd mcp_server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install mcp pymongo pandas plotly kaleido
```

### 2. Run the MCP Server

```bash
cd mcp_server
python3 mongodb_mcp_server.py
```

### 3. Configure Claude Desktop (if using Claude Desktop)

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mongodb-azure": {
      "command": "/path/to/infra/mcp_server/venv/bin/python3",
      "args": ["/path/to/infra/mcp_server/mongodb_mcp_server.py"]
    }
  }
}
```

## 🎯 Quick Examples

### Example 1: Discover Available Fields

**Question:** "What fields can I query in the database?"

**Tool:** `get_available_fields`

**Result:**
```
Standard fields: applicationName, environment, owner, cost, date
Dynamic fields: primaryContact, usage, department, costCenter, team, project
```

---

### Example 2: Find Resources by Primary Contact

**Question:** "Show me all resources for primary contact 'john doe'"

**Tool:** `advanced_query`

**Parameters:**
```json
{
  "filters": {
    "primaryContact": "john doe"
  },
  "limit": 50
}
```

**Result:** List of all resources where primaryContact is "john doe"

---

### Example 3: Cost Breakdown by Department

**Question:** "What's the total cost by department?"

**Tool:** `cost_analysis_by_field`

**Parameters:**
```json
{
  "group_by_field": "department",
  "limit": 10
}
```

**Result:**
```
Department         Total Cost    Avg Cost    Resource Count    % of Total
IT                 $56,789.12    $234.56     242               46.02%
Finance            $34,567.89    $189.23     183               28.00%
HR                 $12,345.67    $145.67     85                10.00%
```

---

### Example 4: Count Resources by Usage Type

**Question:** "How many resources do we have for each usage type?"

**Tool:** `aggregate_by_any_field`

**Parameters:**
```json
{
  "group_by_field": "usage",
  "aggregation_type": "count",
  "limit": 10
}
```

**Result:**
```
Usage                            Count
databricks prod env              1,234
hot storage                      567
analytics                        345
development                      234
```

---

### Example 5: Environment Distribution by Department

**Question:** "Show me a matrix of departments vs environments"

**Tool:** `multi_dimensional_analysis`

**Parameters:**
```json
{
  "field1": "department",
  "field2": "environment"
}
```

**Result:**
```
Department    production    staging    dev    test
IT            120          45         78     23
Finance       56           12         34     8
HR            23           8          15     5
```

---

### Example 6: Find Production Databricks Resources

**Question:** "Show me all production databricks resources in the IT department"

**Tool:** `advanced_query`

**Parameters:**
```json
{
  "filters": {
    "environment": "production",
    "usage": "databricks prod env",
    "department": "IT"
  },
  "fields_to_return": ["applicationName", "cost", "primaryContact", "owner"]
}
```

---

### Example 7: Top Cost Centers

**Question:** "Which cost centers have the highest total cost?"

**Tool:** `cost_analysis_by_field`

**Parameters:**
```json
{
  "group_by_field": "costCenter",
  "limit": 5
}
```

**Result:**
```
Cost Center    Total Cost     Avg Cost    Resource Count
CC123          $89,234.56     $456.78     195
CC456          $67,890.12     $345.67     196
CC789          $45,678.90     $234.56     194
```

---

## 💡 Common Use Cases

### Use Case 1: Ownership Analysis
```
1. get_available_fields → See what ownership fields exist (owner, primaryContact, etc.)
2. aggregate_by_any_field → Count resources by primaryContact
3. cost_analysis_by_field → Calculate total cost by primaryContact
```

### Use Case 2: Cost Optimization
```
1. cost_analysis_by_field → Find highest cost departments
2. advanced_query → Get details of high-cost resources
3. multi_dimensional_analysis → See cost distribution across dimensions
```

### Use Case 3: Resource Distribution
```
1. aggregate_by_any_field → Count resources by environment
2. multi_dimensional_analysis → Cross-reference environment vs department
3. create_bar_chart → Visualize distribution
```

### Use Case 4: Tag Analysis
```
1. get_available_fields → See all extracted tag fields
2. aggregate_by_any_field → Count by specific tag field (usage, project, team)
3. advanced_query → Find resources matching specific tag combinations
```

---

## 🔥 Power User Tips

### Tip 1: Combine Filters
```json
{
  "filters": {
    "environment": "production",
    "department": "IT",
    "date": "2025-11"
  }
}
```

### Tip 2: Use Field Selection
```json
{
  "filters": {"department": "IT"},
  "fields_to_return": ["applicationName", "cost", "owner"]
}
```

### Tip 3: Cost Aggregations
```json
// Sum costs by team
{
  "group_by_field": "team",
  "aggregation_type": "sum",
  "value_field": "cost"
}
```

### Tip 4: Filter Before Grouping
```json
// Cost by department, production only
{
  "group_by_field": "department",
  "filters": {
    "environment": "production"
  }
}
```

### Tip 5: Cross-Tabulation with Filters
```json
// Department vs environment for 2025-11 only
{
  "field1": "department",
  "field2": "environment",
  "filters": {
    "date": "2025-11"
  }
}
```

---

## 📊 All Available Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `get_available_fields` | List all queryable fields | None |
| `advanced_query` | Filter by any field combination | `filters`, `limit`, `fields_to_return` |
| `aggregate_by_any_field` | Group and count/sum/avg | `group_by_field`, `aggregation_type`, `value_field` |
| `cost_analysis_by_field` | Cost breakdown by dimension | `group_by_field`, `filters` |
| `multi_dimensional_analysis` | Cross-tabulate two fields | `field1`, `field2`, `filters` |
| `query_resources` | Basic query (legacy) | `applicationName`, `environment`, `owner` |
| `get_statistics` | Overall database stats | None |
| `get_total_cost` | Total cost with filters | `applicationName`, `environment`, `owner`, `date` |
| `create_bar_chart` | Visualize distribution | `field`, `title`, `limit` |
| `create_pie_chart` | Pie chart visualization | `field`, `title`, `limit` |

---

## 🐛 Troubleshooting

### Issue: "No documents found in database"
**Solution:** Import your Excel data first using the Streamlit UI

### Issue: "Field 'xyz' not found"
**Solution:** Use `get_available_fields` to see what fields exist. Use camelCase (e.g., `primaryContact`, not `Primary Contact`)

### Issue: "Error: value_field is required"
**Solution:** When using `aggregation_type: "sum"` or `"avg"`, you must provide `value_field`

### Issue: MongoDB connection error
**Solution:** Ensure MongoDB is running: `mongod` or `brew services start mongodb-community`

---

## 📚 Learn More

- [MCP_DYNAMIC_QUERY_TOOLS.md](MCP_DYNAMIC_QUERY_TOOLS.md) - Detailed documentation
- [DYNAMIC_PARSING_GUIDE.md](DYNAMIC_PARSING_GUIDE.md) - How tag parsing works
- [MONGODB_DYNAMIC_FIELDS_UPDATE.md](MONGODB_DYNAMIC_FIELDS_UPDATE.md) - MongoDB schema

---

## 🎉 You're Ready!

Start exploring your data with these powerful MCP tools. Remember:

1. **Discover** fields with `get_available_fields`
2. **Filter** data with `advanced_query`
3. **Aggregate** with `aggregate_by_any_field`
4. **Analyze costs** with `cost_analysis_by_field`
5. **Cross-reference** with `multi_dimensional_analysis`

Happy querying! 🚀
