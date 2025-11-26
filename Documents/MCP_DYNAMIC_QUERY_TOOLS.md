# MCP Dynamic Query Tools Documentation

## 🎯 Overview

The MongoDB MCP server has been enhanced with powerful tools to query and analyze data using **ALL dynamically extracted fields** from your tags. You can now slice and dice your data by any dimension - not just the predefined fields.

## 🆕 New Tools

### 1. `get_available_fields`
**Description:** Lists ALL queryable fields in the database, including all dynamically extracted tag fields.

**Parameters:** None

**Returns:**
```json
{
  "total_fields": 12,
  "standard_fields": ["applicationName", "environment", "owner", "cost", "date"],
  "dynamic_fields": ["primaryContact", "usage", "department", "costCenter", "team", "project", "businessUnit"],
  "field_statistics": {
    "primaryContact": {
      "unique_values": 245,
      "non_null_documents": 8543
    },
    "usage": {
      "unique_values": 89,
      "non_null_documents": 4521
    }
    // ... more fields
  },
  "usage_examples": {
    "query_by_field": "Use advanced_query with filters={'fieldName': 'value'}",
    "aggregate_by_field": "Use aggregate_by_any_field with group_by_field='fieldName'",
    "cost_analysis": "Use cost_analysis_by_field with group_by_field='fieldName'"
  }
}
```

**Use Case:** Discover what fields are available for querying and filtering.

---

### 2. `advanced_query`
**Description:** Query resources using ANY combination of fields. Supports all dynamic fields like primaryContact, usage, department, costCenter, etc.

**Parameters:**
- `filters` (required): Dictionary of field:value pairs to filter by
  - Example: `{"primaryContact": "john doe", "department": "IT"}`
- `limit` (optional): Maximum number of results (default: 100)
- `fields_to_return` (optional): List of fields to return (default: all fields)

**Example Request:**
```json
{
  "filters": {
    "primaryContact": "jane doe",
    "department": "IT",
    "environment": "production"
  },
  "limit": 50,
  "fields_to_return": ["applicationName", "cost", "usage"]
}
```

**Returns:**
```json
{
  "filters_applied": {
    "primaryContact": "jane doe",
    "department": "IT",
    "environment": "production"
  },
  "count": 23,
  "limit": 50,
  "results": [
    {
      "applicationName": "app1",
      "cost": 1234.56,
      "usage": "databricks prod"
    }
    // ... more results
  ]
}
```

**Use Cases:**
- Find all resources for a specific primary contact
- Filter by multiple dynamic fields simultaneously
- Get resources matching complex criteria

---

### 3. `aggregate_by_any_field`
**Description:** Count and aggregate documents grouped by ANY field in the database. Can also calculate sum/avg of numeric fields.

**Parameters:**
- `group_by_field` (required): Field to group by
  - Examples: "primaryContact", "department", "usage", "costCenter", "team", "project"
- `aggregation_type` (optional): Type of aggregation - "count" (default), "sum", or "avg"
- `value_field` (optional): Field to sum/avg (required for sum/avg, e.g., "cost")
- `limit` (optional): Maximum number of groups (default: 20)
- `sort_order` (optional): "desc" (default) or "asc"

**Example Request (Count by Department):**
```json
{
  "group_by_field": "department",
  "aggregation_type": "count",
  "limit": 10
}
```

**Example Request (Sum Cost by Primary Contact):**
```json
{
  "group_by_field": "primaryContact",
  "aggregation_type": "sum",
  "value_field": "cost",
  "limit": 20
}
```

**Returns:**
```json
{
  "group_by_field": "department",
  "aggregation_type": "count",
  "value_field": "N/A",
  "results": [
    {"department": "IT", "count": 1234},
    {"department": "Finance", "count": 567},
    {"department": "HR", "count": 89}
  ],
  "total_groups": 3
}
```

**Use Cases:**
- Count resources by any dimension
- Sum costs by department, primary contact, or any other field
- Calculate average costs by usage type

---

### 4. `cost_analysis_by_field`
**Description:** Analyze total cost grouped by any field (e.g., by department, primaryContact, usage, costCenter). Returns detailed cost breakdown with sum, avg, min, max.

**Parameters:**
- `group_by_field` (required): Field to group costs by
- `filters` (optional): Dictionary of filters to apply before grouping
- `limit` (optional): Maximum number of groups (default: 20)

**Example Request:**
```json
{
  "group_by_field": "department",
  "filters": {
    "environment": "production",
    "date": "2025-11"
  },
  "limit": 10
}
```

**Returns:**
```json
{
  "group_by_field": "department",
  "filters_applied": {
    "environment": "production",
    "date": "2025-11"
  },
  "grand_total_cost": 123456.78,
  "results": [
    {
      "department": "IT",
      "totalCost": 56789.12,
      "avgCost": 234.56,
      "minCost": 10.00,
      "maxCost": 5000.00,
      "resourceCount": 242,
      "percentageOfTotal": 46.02
    },
    {
      "department": "Finance",
      "totalCost": 34567.89,
      "avgCost": 189.23,
      "minCost": 5.00,
      "maxCost": 3000.00,
      "resourceCount": 183,
      "percentageOfTotal": 28.00
    }
  ],
  "total_groups": 2
}
```

**Use Cases:**
- Cost breakdown by department
- Identify top spenders by primary contact
- Analyze costs by usage type or project
- Find which cost centers have the highest spend

---

### 5. `multi_dimensional_analysis`
**Description:** Cross-tabulate two fields to analyze relationships (e.g., department vs environment, primaryContact vs applicationName). Creates a matrix showing counts.

**Parameters:**
- `field1` (required): First dimension (rows)
- `field2` (required): Second dimension (columns)
- `filters` (optional): Dictionary of filters to apply
- `limit` (optional): Maximum items per dimension (default: 20)

**Example Request:**
```json
{
  "field1": "department",
  "field2": "environment",
  "filters": {
    "date": "2025-11"
  },
  "limit": 10
}
```

**Returns:**
```json
{
  "field1": "department",
  "field2": "environment",
  "field1_values": ["IT", "Finance", "HR"],
  "field2_values": ["production", "staging", "dev"],
  "filters_applied": {
    "date": "2025-11"
  },
  "matrix": [
    {
      "department": "IT",
      "production": 120,
      "staging": 45,
      "dev": 78
    },
    {
      "department": "Finance",
      "production": 56,
      "staging": 12,
      "dev": 34
    },
    {
      "department": "HR",
      "production": 23,
      "staging": 8,
      "dev": 15
    }
  ],
  "total_combinations": 9
}
```

**Use Cases:**
- See how departments are distributed across environments
- Analyze which primary contacts own which applications
- Cross-reference any two dimensions for pattern discovery

---

## 📊 Real-World Examples

### Example 1: Find All Resources for a Primary Contact
```json
// Tool: advanced_query
{
  "filters": {
    "primaryContact": "john doe"
  },
  "limit": 100
}
```

### Example 2: Cost Breakdown by Usage Type
```json
// Tool: cost_analysis_by_field
{
  "group_by_field": "usage",
  "limit": 10
}
```

### Example 3: Count Resources by Cost Center
```json
// Tool: aggregate_by_any_field
{
  "group_by_field": "costCenter",
  "aggregation_type": "count",
  "limit": 20
}
```

### Example 4: Total Cost by Department (Production Only)
```json
// Tool: cost_analysis_by_field
{
  "group_by_field": "department",
  "filters": {
    "environment": "production"
  },
  "limit": 15
}
```

### Example 5: Cross-Tab of Primary Contact vs Application
```json
// Tool: multi_dimensional_analysis
{
  "field1": "primaryContact",
  "field2": "applicationName",
  "limit": 20
}
```

### Example 6: Average Cost by Team
```json
// Tool: aggregate_by_any_field
{
  "group_by_field": "team",
  "aggregation_type": "avg",
  "value_field": "cost",
  "limit": 10
}
```

### Example 7: Find Databricks Resources in IT Department
```json
// Tool: advanced_query
{
  "filters": {
    "usage": "databricks prod env",
    "department": "IT"
  },
  "fields_to_return": ["applicationName", "owner", "cost", "primaryContact"]
}
```

---

## 🔍 Query Patterns

### Pattern 1: Discovery
1. Use `get_available_fields` to see what fields exist
2. Check field statistics to understand data distribution
3. Decide which fields to query/analyze

### Pattern 2: Filtering
1. Use `advanced_query` with complex filter combinations
2. Narrow down results by multiple criteria
3. Select specific fields to return for focused analysis

### Pattern 3: Aggregation
1. Use `aggregate_by_any_field` to group by a dimension
2. Choose count, sum, or avg based on your needs
3. Sort and limit to see top/bottom results

### Pattern 4: Cost Analysis
1. Use `cost_analysis_by_field` for comprehensive cost breakdown
2. Apply filters to focus on specific subsets
3. Review percentages to identify cost drivers

### Pattern 5: Cross-Analysis
1. Use `multi_dimensional_analysis` to explore relationships
2. Create matrices to visualize patterns
3. Identify correlations between different dimensions

---

## 🚀 Benefits

### ✅ Flexibility
- Query by **ANY** field extracted from tags
- No need to predefine fields
- Works with current and future tag fields automatically

### ✅ Power
- Complex multi-field filtering
- Advanced aggregations (count, sum, avg)
- Cost analysis with detailed breakdowns
- Cross-tabulation for relationship discovery

### ✅ Performance
- MongoDB indexing for fast queries
- Aggregation pipelines for efficient processing
- Limit controls to manage result sizes

### ✅ Insights
- Discover patterns in your data
- Identify cost drivers
- Understand resource distribution
- Track ownership and responsibility

---

## 🛠️ Integration with Claude

These tools are accessible via the MCP protocol, which means Claude can use them directly:

**Example Conversation:**
```
User: "Show me all resources owned by the IT department"

Claude: *Uses advanced_query tool*
{
  "filters": {"department": "IT"},
  "limit": 100
}

User: "What's the total cost breakdown by primary contact?"

Claude: *Uses cost_analysis_by_field tool*
{
  "group_by_field": "primaryContact",
  "limit": 20
}

User: "Which environments does each department use?"

Claude: *Uses multi_dimensional_analysis tool*
{
  "field1": "department",
  "field2": "environment"
}
```

---

## 📝 Best Practices

### 1. Discovery First
Always start with `get_available_fields` to understand what's queryable.

### 2. Use Filters Wisely
Apply filters in `cost_analysis_by_field` and `multi_dimensional_analysis` to focus on relevant data.

### 3. Limit Results
Use the `limit` parameter to avoid overwhelming results, especially for large datasets.

### 4. Field Selection
In `advanced_query`, use `fields_to_return` to get only the data you need.

### 5. Meaningful Grouping
Choose `group_by_field` values that provide business insights (e.g., primaryContact, department, costCenter).

---

## 🔧 Technical Details

### Field Name Format
- MongoDB stores fields in **camelCase** (e.g., `primaryContact`, `costCenter`)
- Original Excel columns are in Title Case (e.g., "Primary Contact", "Cost Center")
- The tools accept camelCase field names

### Null Handling
- Fields with `null` values are grouped as "Unknown"
- Use filters to exclude nulls if needed: `{"field": {"$ne": null}}`

### Cost Conversion
- Cost values are automatically converted to numeric for aggregation
- String costs are converted using `$toDouble`
- Invalid costs default to 0

### Aggregation Pipelines
- All tools use MongoDB aggregation pipelines for efficiency
- Pipelines are optimized with indexes
- Results are sorted and limited server-side

---

## 📚 Related Documentation

- [DYNAMIC_PARSING_GUIDE.md](DYNAMIC_PARSING_GUIDE.md) - How dynamic tag parsing works
- [MONGODB_DYNAMIC_FIELDS_UPDATE.md](MONGODB_DYNAMIC_FIELDS_UPDATE.md) - MongoDB schema changes
- [test_dynamic_mongodb.py](test_dynamic_mongodb.py) - Testing dynamic field insertion

---

## 🎉 Summary

The enhanced MCP tools provide **unlimited flexibility** for querying and analyzing your MongoDB data:

- **5 new tools** for dynamic field operations
- **Query by ANY field** extracted from tags
- **Advanced aggregations** (count, sum, avg)
- **Cost analysis** with detailed breakdowns
- **Cross-tabulation** for pattern discovery
- **Full MCP integration** with Claude

Now you can slice and dice your data in any way imaginable! 🚀
