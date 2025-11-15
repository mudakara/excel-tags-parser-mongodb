# MCP Server Quick Start Guide

Get up and running with the MongoDB MCP server in 5 minutes!

## Prerequisites

- ✅ MongoDB running on `localhost:27017`
- ✅ Data in `azure` database, `resources` collection
- ✅ Python 3.9+ installed

## Step 1: Install Dependencies

```bash
cd mcp_server
pip install -r requirements.txt
pip install kaleido  # Required for chart generation
```

Or use the setup script:
```bash
./setup.sh
```

## Step 2: Test the Server

```bash
# Option 1: Using the test script (easiest)
./run_test.sh

# Option 2: Activate venv first
source venv/bin/activate
python3 test_mcp.py
deactivate

# Option 3: Use venv python directly
venv/bin/python3 test_mcp.py
```

You should see:
```
Testing MongoDB MCP Server...

1. Testing get_database_schema...
✅ Schema retrieved...

2. Testing get_statistics...
✅ Statistics retrieved...

🎉 All tests passed!
```

## Step 3: Choose Your LLM

### Option A: LM Studio (Recommended for Beginners)

1. **Download**: https://lmstudio.ai/
2. **Install a model**: Llama 3.1 8B or Mistral 7B
3. **Add MCP Server**:
   - Settings → Extensions → Enable MCP
   - Add server configuration (see below)
4. **Start chatting!**

### Option B: Claude Desktop

1. **Edit config file**:
   ```bash
   # macOS
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Add this**:
   ```json
   {
     "mcpServers": {
       "mongodb-azure-analytics": {
         "command": "python3",
         "args": ["/absolute/path/to/mcp_server/mongodb_mcp_server.py"]
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### Option C: Continue.dev (VS Code)

1. **Install Continue extension** in VS Code
2. **Configure** (Cmd/Ctrl+Shift+P → "Continue: Open Config"):
   ```json
   {
     "mcpServers": [
       {
         "name": "mongodb-azure-analytics",
         "command": "python3",
         "args": ["/absolute/path/to/mcp_server/mongodb_mcp_server.py"]
       }
     ]
   }
   ```
3. **Reload VS Code**

## Step 4: Try It Out!

Ask your LLM:

```
"Show me database statistics"
```

```
"Create a bar chart of resources by environment"
```

```
"Which owner has the most resources?"
```

## Common Issues

### "Cannot connect to MongoDB"
```bash
brew services start mongodb-community
```

### "No module named 'mcp'"
```bash
pip install mcp
```

### "Charts not generating"
```bash
pip install kaleido
```

### "LLM doesn't see the server"
- Use **absolute paths** in config (not relative)
- Restart the LLM application
- Check `python --version` matches what's in config

## Next Steps

1. **Read full docs**: `README.md`
2. **Try example prompts**: `PROMPTS.md`
3. **Customize tools**: Edit `mongodb_mcp_server.py`

## Example Session

```
You: "Show me database statistics"
LLM: [Returns statistics: 1000 documents, 50 apps, 3 environments, 25 owners]

You: "Create a bar chart showing resource distribution by environment"
LLM: [Generates and displays a bar chart]

You: "Which applications are in production?"
LLM: [Queries and lists production applications]

You: "Make a heatmap of apps across environments"
LLM: [Creates a heatmap visualization]
```

That's it! You're ready to analyze your Azure resources with AI. 🎉
