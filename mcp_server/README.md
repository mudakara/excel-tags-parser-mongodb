# MongoDB MCP Server for Azure Resources Analytics

This MCP (Model Context Protocol) server allows open-source LLMs to query your MongoDB database and create charts/reports based on Azure resources data.

## Features

- **Database Querying**: Query resources by application, environment, owner
- **Statistics & Aggregations**: Get counts, distributions, and breakdowns
- **Chart Generation**: Automatically create bar charts, pie charts, and heatmaps
- **LLM Integration**: Works with any MCP-compatible LLM client

## Available Tools

The MCP server exposes 8 tools that LLMs can use:

### 1. `get_database_schema`
Get the database schema and structure with sample documents.

**Usage**: "Show me the database schema"

### 2. `query_resources`
Query resources with filters.

**Parameters**:
- `applicationName` (optional): Filter by application
- `environment` (optional): Filter by environment
- `owner` (optional): Filter by owner
- `limit` (optional): Max results (default: 100)

**Usage**: "Show me all production resources for app X"

### 3. `get_statistics`
Get overall database statistics.

**Usage**: "Give me database statistics"

### 4. `aggregate_by_field`
Count documents grouped by field.

**Parameters**:
- `field` (required): One of `applicationName`, `environment`, `owner`
- `limit` (optional): Max groups (default: 20)

**Usage**: "How many resources per environment?"

### 5. `create_bar_chart`
Create a bar chart showing distribution.

**Parameters**:
- `field` (required): Field to chart
- `title` (optional): Chart title
- `limit` (optional): Top N items (default: 15)

**Usage**: "Create a bar chart of resources by application"

### 6. `create_pie_chart`
Create a pie chart showing distribution.

**Parameters**:
- `field` (required): Field to chart
- `title` (optional): Chart title
- `limit` (optional): Top N items (default: 10)

**Usage**: "Show a pie chart of resource distribution by environment"

### 7. `create_environment_app_matrix`
Create a heatmap of applications across environments.

**Parameters**:
- `title` (optional): Chart title

**Usage**: "Create a heatmap showing which apps are in which environments"

### 8. `get_resources_by_owner`
Get detailed breakdown by owner.

**Parameters**:
- `limit` (optional): Number of owners (default: 10)

**Usage**: "Show me what resources each owner has"

## Installation

### 1. Install Dependencies

```bash
cd mcp_server
pip install -r requirements.txt
```

### 2. Install Kaleido for Chart Generation

Kaleido is required for plotly to generate static images:

```bash
pip install kaleido
```

### 3. Verify MongoDB is Running

```bash
mongosh --eval "db.adminCommand('ping')"
```

## Setup with Open-Source LLMs

### Option 1: Using Claude Desktop (with Claude Code)

1. **Locate Claude Desktop config**:
   ```bash
   # macOS
   ~/Library/Application Support/Claude/claude_desktop_config.json

   # Windows
   %APPDATA%\Claude\claude_desktop_config.json

   # Linux
   ~/.config/Claude/claude_desktop_config.json
   ```

2. **Add MCP server configuration**:
   ```json
   {
     "mcpServers": {
       "mongodb-azure-analytics": {
         "command": "python3",
         "args": ["/absolute/path/to/infra/mcp_server/mongodb_mcp_server.py"]
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Verify**: Look for 🔌 icon in Claude showing MCP servers connected

### Option 2: Using LM Studio (Open-Source LLMs)

LM Studio has built-in MCP support:

1. **Download LM Studio**: https://lmstudio.ai/

2. **Download an open-source model**:
   - Llama 3.1 (8B or 70B)
   - Mistral 7B
   - Qwen 2.5

3. **Enable MCP in LM Studio**:
   - Go to Settings → Extensions
   - Enable "Model Context Protocol"

4. **Add server config**:
   ```json
   {
     "mongodb-azure-analytics": {
       "command": "python3",
       "args": ["/absolute/path/to/mcp_server/mongodb_mcp_server.py"]
     }
   }
   ```

5. **Start chatting** - the model can now use MongoDB tools!

### Option 3: Using Continue.dev (VS Code Extension)

Continue.dev is a VS Code extension for open-source LLMs with MCP support:

1. **Install Continue extension** in VS Code

2. **Configure** in `.continue/config.json`:
   ```json
   {
     "models": [
       {
         "title": "Llama 3.1",
         "provider": "ollama",
         "model": "llama3.1:8b"
       }
     ],
     "mcpServers": [
       {
         "name": "mongodb-azure-analytics",
         "command": "python3",
         "args": ["/absolute/path/to/mcp_server/mongodb_mcp_server.py"]
       }
     ]
   }
   ```

3. **Restart VS Code**

### Option 4: Using Ollama Directly

1. **Install Ollama**: https://ollama.ai/

2. **Pull a model**:
   ```bash
   ollama pull llama3.1
   ```

3. **Use with Open Interpreter**:
   ```bash
   pip install open-interpreter
   interpreter --model ollama/llama3.1 --mcp mongodb-azure-analytics
   ```

## Usage Examples

Once connected to an LLM, you can ask natural language questions:

### Querying Data

```
User: "Show me all production resources"
LLM: Uses query_resources with environment="production"

User: "How many resources does John own?"
LLM: Uses query_resources with owner="John"

User: "Get database statistics"
LLM: Uses get_statistics
```

### Creating Charts

```
User: "Create a bar chart showing resource distribution by environment"
LLM: Uses create_bar_chart with field="environment"

User: "Show me a pie chart of the top 10 applications"
LLM: Uses create_pie_chart with field="applicationName", limit=10

User: "Create a heatmap of applications across environments"
LLM: Uses create_environment_app_matrix
```

### Analysis

```
User: "Which owner has the most resources?"
LLM: Uses get_resources_by_owner

User: "How many unique applications are in production?"
LLM: Uses query_resources + aggregation

User: "Show me resource distribution across all environments"
LLM: Uses aggregate_by_field with field="environment"
```

## Testing the MCP Server

### Manual Testing

Run the server directly to test:

```bash
cd mcp_server
python mongodb_mcp_server.py
```

Then send MCP commands via stdio (advanced).

### Testing with Python

```python
import asyncio
from mongodb_mcp_server import get_statistics, query_resources

# Test statistics
async def test():
    stats = await get_statistics()
    print(stats)

asyncio.run(test())
```

## Troubleshooting

### Error: "Cannot connect to MongoDB"

**Solution**:
```bash
# Check if MongoDB is running
brew services list | grep mongodb

# Start MongoDB if not running
brew services start mongodb-community
```

### Error: "ModuleNotFoundError: No module named 'mcp'"

**Solution**:
```bash
pip install mcp
```

### Charts Not Generating

**Solution**:
```bash
# Install kaleido
pip install kaleido

# Verify
python -c "import plotly.io as pio; print(pio.kaleido)"
```

### LLM Not Detecting MCP Server

**Solution**:
1. Verify config path is absolute (not relative)
2. Check Python is in PATH
3. Restart the LLM application
4. Check logs for errors

## Example Prompts for LLMs

Here are some effective prompts to use with your LLM:

### Basic Queries
- "What's the database schema?"
- "Show me the first 10 resources"
- "How many total resources are in the database?"

### Filtering
- "Show me all dev environment resources"
- "List resources owned by [name]"
- "Find all resources for application [appname]"

### Statistics
- "How many unique applications do we have?"
- "What are the different environments?"
- "Which owner has the most resources?"

### Visualizations
- "Create a bar chart of resources by environment"
- "Show a pie chart of top 15 applications"
- "Make a heatmap of applications vs environments"
- "Visualize resource distribution by owner"

### Analysis
- "Compare production vs development resources"
- "Which applications are in multiple environments?"
- "Break down resources by owner with details"
- "Show me the top 10 applications by resource count"

### Combined
- "Show me production resources owned by John and create a chart"
- "Analyze the distribution of resources across environments and create visualizations"
- "Give me statistics and a breakdown by application with charts"

## Advanced Configuration

### Custom MongoDB URI

Edit `mongodb_mcp_server.py`:

```python
MONGODB_URI = "mongodb://username:password@host:port/"
MONGODB_DATABASE = "your_database"
MONGODB_COLLECTION = "your_collection"
```

### Custom Chart Styling

Modify the plotly configuration in chart functions:

```python
fig.update_layout(
    template="plotly_dark",  # Dark theme
    font=dict(size=14),
    title_font_size=20
)
```

### Adding New Tools

Add new tool definitions in `list_tools()` and implement in `call_tool()`:

```python
Tool(
    name="your_new_tool",
    description="What your tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First parameter"}
        },
        "required": ["param1"]
    }
)
```

## Security Considerations

For production use:

1. **Authentication**: Add MongoDB authentication
2. **Rate Limiting**: Implement query rate limits
3. **Input Validation**: Sanitize all inputs
4. **Access Control**: Limit which collections can be accessed
5. **Logging**: Add audit logging for all queries

## Performance Tips

1. **Indexes**: Ensure MongoDB has indexes on frequently queried fields
2. **Limits**: Always use limits for large datasets
3. **Caching**: Consider caching frequently accessed statistics
4. **Pagination**: Implement pagination for large result sets

## Integration with Dashboards

The charts generated can be saved and integrated into dashboards:

```python
# Save chart as HTML
fig.write_html("chart.html")

# Save as static image
fig.write_image("chart.png")

# Embed in Streamlit
import streamlit as st
st.plotly_chart(fig)
```

## Next Steps

1. **Deploy to Production**: Run as a service with systemd/supervisor
2. **Add More Tools**: Custom aggregations, complex queries
3. **Real-time Updates**: Add WebSocket support for live data
4. **Multi-Database**: Support multiple MongoDB databases
5. **Export Features**: Add CSV, Excel, PDF export tools

## Support

For issues or questions:
1. Check MongoDB connection
2. Verify MCP server is running
3. Check LLM logs for errors
4. Test tools individually

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [Plotly Charts](https://plotly.com/python/)
- [LM Studio](https://lmstudio.ai/)
- [Continue.dev](https://continue.dev/)
