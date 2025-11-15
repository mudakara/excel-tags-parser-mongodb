# Prompt Examples for Azure Resources Analytics

This guide provides example prompts you can use with your LLM to analyze Azure resources data.

## Getting Started

### Understanding the Data
```
"What's in the database? Show me the schema."
"How many total resources do we have?"
"What are the unique environments in the database?"
"List all application names we have."
```

## Querying Resources

### Basic Queries
```
"Show me all production resources"
"Find all dev environment resources"
"List all resources owned by John"
"Get all resources for the 'webapp' application"
```

### Filtered Queries
```
"Show me production resources for the 'api' application"
"Find dev resources owned by Sarah"
"List all resources in staging environment"
"Get resources for application 'frontend' in production"
```

### Limiting Results
```
"Show me the first 10 resources"
"Get 20 production resources"
"List 5 resources owned by each owner"
```

## Statistics & Counts

### Overall Statistics
```
"Give me database statistics"
"How many unique applications are there?"
"How many different owners do we have?"
"What environments exist in the database?"
```

### Grouping & Counting
```
"Count resources by environment"
"How many resources per application?"
"Show resource distribution by owner"
"Group resources by environment and count them"
```

### Top N Queries
```
"Which are the top 10 applications by resource count?"
"Show me the top 5 owners with most resources"
"What are the 3 most common environments?"
```

## Visualization Requests

### Bar Charts
```
"Create a bar chart of resources by environment"
"Make a bar chart showing top 15 applications"
"Visualize resource distribution by owner as a bar chart"
"Show a bar chart of application counts"
```

### Pie Charts
```
"Create a pie chart of environment distribution"
"Make a pie chart showing top 10 applications"
"Show resource ownership as a pie chart"
"Visualize the percentage of resources per environment"
```

### Heatmaps
```
"Create a heatmap of applications across environments"
"Show which applications are in which environments as a heatmap"
"Make an environment vs application matrix"
```

## Analysis Requests

### Comparative Analysis
```
"Compare production vs development resource counts"
"Which environment has the most resources?"
"What's the difference between prod and dev resources?"
```

### Ownership Analysis
```
"Who owns the most resources?"
"Break down resources by owner with details"
"Show me what each owner is responsible for"
"Which owner has resources in the most environments?"
```

### Application Analysis
```
"Which applications are in multiple environments?"
"What environments does 'webapp' exist in?"
"Show me applications that are only in production"
"Find applications with resources in dev but not in prod"
```

## Combined Requests

### Query + Visualization
```
"Show production resources and create a bar chart by application"
"Find all resources owned by John and visualize them"
"Get environment distribution and make a pie chart"
```

### Statistics + Charts
```
"Give me database statistics and create visualizations"
"Show resource counts by environment with both numbers and charts"
"Analyze application distribution with stats and a bar chart"
```

### Multi-step Analysis
```
"First show me database stats, then create charts for environment and application distribution"
"Get the top 10 applications and create both bar and pie charts"
"Show resource breakdown by owner and visualize the top 5"
```

## Reporting Requests

### Summary Reports
```
"Create a summary report of the database"
"Give me an executive summary of our Azure resources"
"Provide an overview with key metrics and visualizations"
```

### Detailed Reports
```
"Generate a detailed report on production resources"
"Create a comprehensive analysis of resource ownership"
"Make a full report on application distribution"
```

### Specific Focus Reports
```
"Report on 'webapp' application across all environments"
"Analyze John's resources with details and charts"
"Create a production environment report with statistics"
```

## Trend & Pattern Analysis

### Pattern Detection
```
"Are there any resources without owners?"
"Find applications that exist in all environments"
"Show resources that might be duplicated"
"Identify unusual patterns in the data"
```

### Resource Distribution
```
"How evenly are resources distributed across owners?"
"Which environments are most/least used?"
"What's the typical number of resources per application?"
```

## Export & Documentation

### Data Export Requests
```
"Export production resources to a format I can analyze"
"Give me a CSV-like view of all resources"
"Format the data for a spreadsheet"
```

### Documentation
```
"Document the database structure"
"Create a data dictionary"
"Explain what each field means with examples"
```

## Troubleshooting Queries

### Data Quality
```
"Find resources with missing information"
"Check for NULL values in important fields"
"Validate data completeness"
"Show resources with empty tags"
```

### Consistency Checks
```
"Check if environment names are consistent"
"Look for duplicate application names"
"Verify owner information is complete"
```

## Advanced Queries

### Complex Filters
```
"Show production resources for applications starting with 'web' owned by John"
"Find resources in dev or staging but not in production"
"Get all resources except those owned by system accounts"
```

### Custom Aggregations
```
"For each owner, show their top 3 applications by resource count"
"Group by environment and show average resources per application"
"Calculate the ratio of production to non-production resources"
```

### Time-based Queries (if import dates exist)
```
"Show resources imported in the last week"
"Compare imports from different dates"
"What was imported most recently?"
```

## Tips for Better Results

1. **Be Specific**: Instead of "show resources", say "show production resources for webapp"
2. **Request Visualizations**: Always ask for charts when analyzing distributions
3. **Set Limits**: For large datasets, specify limits (e.g., "top 10")
4. **Combine Requests**: Ask for both data and visualization in one prompt
5. **Use Field Names**: Use exact field names: `applicationName`, `environment`, `owner`

## Sample Multi-Turn Conversations

### Example 1: Environment Analysis
```
You: "How many environments do we have?"
LLM: Uses get_statistics, shows environments

You: "Create a bar chart of resource distribution by environment"
LLM: Uses create_bar_chart with field="environment"

You: "Which environment has the most resources?"
LLM: Uses aggregate_by_field, identifies top environment
```

### Example 2: Application Deep Dive
```
You: "What are the top 5 applications?"
LLM: Uses aggregate_by_field with limit=5

You: "Show details for the top application"
LLM: Uses query_resources for that application

You: "Create visualizations for this application"
LLM: Creates charts showing distribution
```

### Example 3: Ownership Analysis
```
You: "Who are the resource owners?"
LLM: Uses get_statistics to show owners

You: "Break down resources by owner"
LLM: Uses get_resources_by_owner

You: "Create a pie chart of owner distribution"
LLM: Uses create_pie_chart with field="owner"
```

## Quick Reference

| What You Want | Example Prompt |
|---------------|----------------|
| Database overview | "Show database schema and statistics" |
| List resources | "Show all production resources" |
| Count something | "Count resources by environment" |
| Make a bar chart | "Create bar chart of top 10 applications" |
| Make a pie chart | "Show pie chart of environment distribution" |
| Make a heatmap | "Create heatmap of apps vs environments" |
| Analyze ownership | "Break down resources by owner" |
| Find patterns | "Which apps are in multiple environments?" |
| Compare data | "Compare prod vs dev resource counts" |
| Export data | "Show me all resources in table format" |
