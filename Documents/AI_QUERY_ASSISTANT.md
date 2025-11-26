# AI Query Assistant - Home Page

## 🎯 Overview

The Home page has been transformed into a powerful **AI Query Assistant** that uses Large Language Models (LLMs) to query your MongoDB data using natural language. The AI has access to all MongoDB MCP tools and can intelligently query, aggregate, and analyze your data.

## ✨ Key Features

- **🤖 Multiple LLM Support**: Connect to OpenRouter, Claude, or custom LLMs
- **💬 Natural Language Queries**: Ask questions in plain English
- **🔧 MCP Tool Integration**: AI automatically uses MongoDB tools to answer questions
- **📊 Smart Analysis**: Get insights, aggregations, and cost analysis
- **🎨 Interactive Chat**: ChatGPT-style interface with message history
- **🔍 Transparent Tool Calls**: See exactly which tools the AI uses

## 🚀 Getting Started

### 1. Choose Your LLM Provider

#### Option A: OpenRouter (Recommended)
- **Benefits**: Access to multiple models, pay-per-use pricing
- **Setup**:
  1. Sign up at https://openrouter.ai/
  2. Get your API key from the dashboard
  3. Add credits to your account
  4. Select from 20+ models including Claude, GPT-4, Llama, Gemini

#### Option B: Claude Direct
- **Benefits**: Direct access to Claude 3.5 Sonnet
- **Setup**:
  1. Sign up at https://console.anthropic.com/
  2. Get your API key
  3. Add credits to your account

#### Option C: Custom LLM (Coming Soon)
- Connect to self-hosted models
- LM Studio, Ollama, vLLM support

### 2. Configure the Assistant

1. **Open the Home page**
   ```bash
   streamlit run src/ui/streamlit_app.py
   ```

2. **Select LLM Provider** in the sidebar
   - Choose OpenRouter, Claude, or Custom

3. **Enter API Key**
   - Paste your API key (stored securely in session)

4. **Select Model** (OpenRouter only)
   - Choose from available models:
     - `anthropic/claude-3.5-sonnet` (Recommended)
     - `openai/gpt-4-turbo`
     - `meta-llama/llama-3.1-70b-instruct`
     - And many more!

5. **Verify MongoDB Connection**
   - Ensure MongoDB status shows "✅ Connected"

### 3. Start Asking Questions!

Type natural language questions in the chat input. Examples below.

## 💡 Example Questions

### Basic Queries

**Question:** "What fields can I query in the database?"
```
The AI will use get_available_fields() tool to list all queryable fields
```

**Question:** "Show me all resources in the IT department"
```
The AI will use advanced_query() with filters={'department': 'IT'}
```

**Question:** "How many resources do we have by environment?"
```
The AI will use aggregate_by_any_field() grouped by environment
```

### Cost Analysis

**Question:** "What's the total cost by department?"
```
The AI will use cost_analysis_by_field() with group_by_field='department'
```

**Question:** "Show me the top 5 cost centers by total spend"
```
The AI will use cost_analysis_by_field() with group_by_field='costCenter', limit=5
```

**Question:** "What's the total cost for production environment?"
```
The AI will use get_total_cost() with environment='production'
```

### Complex Analysis

**Question:** "Which primary contact owns the most resources?"
```
The AI will use aggregate_by_any_field() to count by primaryContact
```

**Question:** "Show me production resources for the IT department with costs over $1000"
```
The AI will construct a complex query using advanced_query() with multiple filters
```

**Question:** "Analyze costs by usage type and show me the top 3"
```
The AI will use cost_analysis_by_field() grouped by usage, limited to 3
```

### Insights & Recommendations

**Question:** "What are our biggest cost drivers?"
```
The AI will run multiple queries and provide analysis
```

**Question:** "Find resources that might be untagged or misconfigured"
```
The AI will query for null/missing fields and analyze results
```

**Question:** "Give me a summary of our database"
```
The AI will use get_statistics() and format a comprehensive summary
```

## 🔧 Available MCP Tools

The AI has access to these MongoDB tools:

| Tool | Purpose |
|------|---------|
| `get_available_fields` | List all queryable fields |
| `advanced_query` | Filter by any field combination |
| `aggregate_by_any_field` | Group and count/sum/avg by any field |
| `cost_analysis_by_field` | Detailed cost breakdown by dimension |
| `get_statistics` | Database overview statistics |
| `get_total_cost` | Calculate total costs with filters |

The AI automatically chooses which tools to use based on your question!

## 🎨 User Interface

### Chat Interface

```
┌─────────────────────────────────────────┐
│  User: "What's the total cost by dept?" │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  🔧 Executing Tools...                   │
│  Calling: cost_analysis_by_field         │
│  Parameters: {"group_by_field": "dept"}  │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  Assistant: Based on the analysis...     │
│                                          │
│  Department | Total Cost | % of Total   │
│  -----------|------------|-------------  │
│  IT         | $56,789    | 46%          │
│  Finance    | $34,567    | 28%          │
│  HR         | $12,345    | 10%          │
│                                          │
│  The IT department has the highest...   │
└─────────────────────────────────────────┘
```

### Sidebar

- **LLM Provider Selection**
- **API Key Input** (secure, not saved)
- **Model Selection** (for OpenRouter)
- **MongoDB Connection Status**
- **Available MCP Tools** (expandable list)

### Tool Execution (Expandable)

When the AI uses tools, you can expand to see:
- Tool name
- Parameters passed
- Raw results returned

This provides transparency into how the AI answers your questions.

## 🔐 Security & Privacy

### API Keys
- **Stored in MongoDB** - persists across page refreshes for convenience
- **Not logged** - API keys are never written to logs
- **User-specific** - each user has their own settings (user_id: "default")

### Data
- All queries run against your **local MongoDB**
- No data sent to external services except LLM API calls
- Tool results are formatted before sending to LLM
- You control what data the LLM sees

### Managing Saved Settings

Your LLM configuration (provider, API key, model) is automatically saved to MongoDB and will persist across page refreshes.

**To clear saved settings:**
```python
# Run in Python console or create a script
from src.database.settings_manager import clear_llm_settings
clear_llm_settings()  # Clears settings for default user
```

**To view saved settings:**
```python
from src.database.settings_manager import load_llm_settings
settings = load_llm_settings()
print(settings)
```

### Best Practices
1. Rotate API keys regularly using the sidebar
2. Monitor API usage on provider dashboards
3. Limit API key permissions if possible
4. Clear settings if sharing the application with others

## 💰 Cost Considerations

### OpenRouter Pricing (as of 2024)
- **Claude 3.5 Sonnet**: ~$3-6 per million tokens
- **GPT-4 Turbo**: ~$10-30 per million tokens
- **Llama 3.1 70B**: ~$0.50-2 per million tokens

### Typical Query Costs
- Simple query: $0.001 - $0.005 (less than 1 cent)
- Complex multi-tool query: $0.01 - $0.05 (1-5 cents)
- Analysis with multiple iterations: $0.10 - $0.25 (10-25 cents)

### Cost Optimization Tips
1. Use cheaper models for simple queries (Llama, GPT-3.5)
2. Use premium models (Claude, GPT-4) for complex analysis
3. Clear chat history periodically (reduces context size)
4. Be specific in questions to reduce tool calls
5. Monitor usage on your provider dashboard

## 🎯 Use Cases

### 1. Data Exploration
"What fields are available in my data?"
"Show me a sample of resources with all their fields"
"List all unique departments"

### 2. Cost Management
"What's our total cloud spend this month?"
"Which team has the highest costs?"
"Show me cost trends by environment"

### 3. Resource Inventory
"How many resources do we have?"
"What's the distribution of resources by owner?"
"Find all production resources"

### 4. Compliance & Governance
"Which resources don't have an owner tagged?"
"Find resources missing cost center information"
"Show me resources that aren't in our standard environments"

### 5. Analysis & Insights
"What are our top 5 cost drivers?"
"Which applications consume the most resources?"
"Analyze usage patterns across departments"

## 🐛 Troubleshooting

### "Please enter your API key"
**Solution:** Enter your OpenRouter or Claude API key in the sidebar

### "Cannot connect to MongoDB"
**Solution:** Start MongoDB: `brew services start mongodb-community` or `mongod`

### "Error calling tool"
**Solution:**
- Check MongoDB is running and has data
- Verify tool parameters are correct
- Check logs for detailed error messages

### "API Error: Unauthorized"
**Solution:**
- Verify your API key is correct
- Check API key has sufficient credits
- Ensure API key has proper permissions

### "Response is empty"
**Solution:**
- Model might not support tools (try Claude or GPT-4)
- Try rephrasing your question
- Check tool calls in the expander

### "Too many iterations"
**Solution:**
- Query timed out after 5 tool call iterations
- Try breaking question into smaller parts
- Simplify the query

## 🔄 How It Works

### Architecture

```
┌─────────┐     ┌─────────────┐     ┌──────────────┐
│  User   │────▶│  Streamlit  │────▶│  LLM API     │
│ Question│     │   (Home)    │     │ (OpenRouter/ │
└─────────┘     └─────────────┘     │  Claude)     │
                       │             └──────────────┘
                       │                     │
                       ▼                     │
                ┌─────────────┐             │
                │  MCP Tools  │◀────────────┘
                │  (MongoDB)  │  Tool Calls
                └─────────────┘
                       │
                       ▼
                ┌─────────────┐
                │   MongoDB   │
                └─────────────┘
```

### Flow

1. **User asks question** → Sent to chat interface
2. **Streamlit calls LLM API** → Passes question + available tools
3. **LLM decides which tools to use** → Returns tool calls
4. **Streamlit executes MCP tools** → Calls MongoDB functions
5. **Results returned to LLM** → LLM formats answer
6. **Answer displayed to user** → Formatted response shown

### Tool Calling Process

1. LLM receives user question
2. LLM decides if tools are needed
3. If yes, LLM returns tool calls with parameters
4. Streamlit executes each tool call
5. Results sent back to LLM
6. LLM uses results to formulate answer
7. Final answer displayed to user

## 📚 Advanced Tips

### 1. Chain Multiple Questions

You can ask follow-up questions that build on previous context:

```
User: "What fields are available?"
AI: [Lists all fields]

User: "Show me top 5 by primaryContact"
AI: [Uses context to query primaryContact field]
```

### 2. Request Specific Formats

```
User: "Show me cost by department as a table"
User: "Give me the results in JSON format"
User: "Create a bullet list of all environments"
```

### 3. Ask for Explanations

```
User: "Why is the IT department cost so high?"
User: "Explain the difference between these two cost centers"
User: "What does this data tell us about our resource allocation?"
```

### 4. Combine Queries

```
User: "Show me production costs and compare with staging"
User: "Find resources owned by John and analyze their costs"
User: "Give me a breakdown by department and environment"
```

## 🎓 Best Practices

### Writing Effective Questions

✅ **Good Questions:**
- "What's the total cost by department?"
- "Show me all IT resources in production"
- "Find resources without a cost center"

❌ **Avoid:**
- "Tell me everything" (too broad)
- Single word queries without context
- Vague requests like "analyze data"

### Getting Better Answers

1. **Be specific** - "production environment" vs "prod"
2. **Use field names** - if you know them
3. **Set limits** - "top 10" vs "all"
4. **Provide context** - mention what you're looking for
5. **Ask follow-ups** - refine based on initial answers

## 🆕 What's Next

Future enhancements planned:

- [ ] Chart generation directly in chat
- [ ] Export query results to CSV/Excel
- [ ] Save favorite queries
- [ ] Query templates
- [ ] Multi-database support
- [ ] Streaming responses
- [ ] Voice input support

## 📞 Support

For issues:
1. Check MongoDB connection
2. Verify API key is valid
3. Review error messages in tool call expander
4. Check application logs
5. Open an issue on GitHub

---

**Powered by AI + MongoDB + MCP** 🚀
