# AI Assistant Setup Guide

## 🚀 Quick Setup (5 minutes)

Follow these steps to get the AI Query Assistant running:

### Step 1: Install Dependencies

```bash
cd /Users/davisgeorge/Documents/Claude/infra
pip3 install -r requirements.txt --break-system-packages
```

This installs all required libraries including:
- `requests` - for LLM API calls
- `mcp` - for MCP server functionality
- `streamlit` - for the web interface
- `pymongo` - for MongoDB connection
- `pandas`, `plotly` - for data processing and visualization

**Note:** The `--break-system-packages` flag is needed on macOS to install Python packages.

### Step 2: Start MongoDB

```bash
# macOS (Homebrew)
brew services start mongodb-community

# Or run directly
mongod
```

### Step 3: Get an API Key

Choose **ONE** of these options:

#### Option A: OpenRouter (Recommended for beginners)

1. Go to https://openrouter.ai/
2. Click "Sign In" → Sign up with Google/GitHub
3. Go to "Keys" in the dashboard
4. Click "Create Key"
5. Copy your API key (starts with `sk-or-v1-...`)
6. Add $5-10 credits to your account

**Why OpenRouter?**
- Access to 20+ models
- Pay only for what you use
- No monthly subscription
- Great for testing different models

#### Option B: Claude Direct

1. Go to https://console.anthropic.com/
2. Sign up for an account
3. Go to "API Keys"
4. Click "Create Key"
5. Copy your API key (starts with `sk-ant-...`)
6. Add credits to your account

**Why Claude Direct?**
- Direct access to Claude 3.5 Sonnet
- Best quality for complex queries
- Excellent tool use capabilities

### Step 4: Run the Application

```bash
streamlit run src/ui/streamlit_app.py
```

The app will open in your browser at http://localhost:8501

### Step 5: Configure the AI

1. **Select LLM Provider** in the sidebar
   - Choose "OpenRouter" or "Claude"

2. **Enter Your API Key**
   - Paste the API key you copied
   - It's stored securely in MongoDB and persists across page refreshes

3. **Select Model** (OpenRouter only)
   - For beginners: `anthropic/claude-3.5-sonnet`
   - For cost-saving: `meta-llama/llama-3.1-70b-instruct`
   - For best quality: `openai/gpt-4-turbo`

4. **Verify MongoDB Status**
   - Sidebar should show "✅ Connected"

### Step 6: Test It!

Try these starter questions:

```
"What fields can I query in the database?"
```

```
"How many resources do we have in total?"
```

```
"Show me the total cost by department"
```

## 📋 Detailed Setup

### Prerequisites

- ✅ Python 3.8+
- ✅ MongoDB 4.0+ (running locally)
- ✅ Data in MongoDB (upload via Excel Upload page first)
- ✅ API key from OpenRouter or Claude

### Testing Your Setup

1. **Test MongoDB Connection**
   ```bash
   mongosh
   use azure
   db.resources.countDocuments()
   ```
   Should return a count > 0

2. **Test API Key**
   - Enter API key in sidebar
   - Ask a simple question
   - Should get a response

3. **Test Tool Calls**
   - Ask "What fields are available?"
   - Expand "🔧 Executing Tools..."
   - Should see `get_available_fields` call

## 🔧 Configuration Options

### Environment Variables (Optional)

For production, you can set API keys via environment variables:

```bash
# ~/.bashrc or ~/.zshrc
export OPENROUTER_API_KEY="sk-or-v1-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

Then modify Home.py to read from environment:

```python
import os
api_key = os.getenv("OPENROUTER_API_KEY") or st.text_input(...)
```

### Model Selection Guide

**For Simple Queries:**
- `meta-llama/llama-3.1-70b-instruct` - Fast, cheap
- `openai/gpt-3.5-turbo` - Reliable, affordable

**For Complex Analysis:**
- `anthropic/claude-3.5-sonnet` - Best overall
- `openai/gpt-4-turbo` - Excellent reasoning

**For Cost-Conscious:**
- `meta-llama/llama-3.1-70b-instruct` - $0.50/M tokens
- `google/gemini-pro-1.5` - $1-2/M tokens

**For Best Quality:**
- `anthropic/claude-3-opus` - Most capable
- `openai/gpt-4` - Most reliable

### Usage Limits

**Free Tier:**
- OpenRouter: No free tier (pay-as-you-go)
- Claude: $5 free credits for new users

**Recommended Starting Budget:**
- $5-10 for testing (100-200 queries)
- $20-50 for regular use (500-1000 queries)
- $100+ for heavy use (2000+ queries)

## 🎯 Sample Workflow

### First Time Setup

1. **Upload Data** (if not done already)
   - Go to "Excel Upload" page
   - Upload your Excel file
   - Click "Process File"
   - Click "Push to MongoDB"

2. **Get API Key**
   - Sign up at OpenRouter.ai
   - Add $5 credits
   - Copy API key

3. **Test the AI**
   - Go to Home page
   - Enter API key
   - Ask: "What's in my database?"

4. **Explore**
   - Try different questions
   - Watch tool calls in action
   - Refine your queries

### Daily Usage

1. Start MongoDB (if not running)
2. Run Streamlit app
3. Enter API key (if new session)
4. Start asking questions!

## 🐛 Common Issues

### "Cannot connect to MongoDB"

**Solution:**
```bash
# Check if MongoDB is running
brew services list | grep mongodb

# Start if needed
brew services start mongodb-community

# Or
mongod
```

### "Invalid API Key"

**Solutions:**
- Double-check you copied the entire key
- Ensure key starts with `sk-or-v1-` (OpenRouter) or `sk-ant-` (Claude)
- Verify key hasn't been revoked
- Check you have credits in your account

### "No documents found in database"

**Solution:**
1. Go to "Excel Upload" page
2. Upload and process an Excel file
3. Push data to MongoDB
4. Return to Home page

### "Tool execution failed"

**Solutions:**
- Check MongoDB has data: `db.resources.findOne()`
- Verify field names in query match database
- Check logs for detailed error

### "API request timeout"

**Solutions:**
- Check internet connection
- Try again (might be temporary API issue)
- Try a different model
- Simplify your question

### "ModuleNotFoundError: No module named 'mcp'"

**Solution:**
```bash
# Install the MCP package
pip3 install mcp --break-system-packages

# Or reinstall all dependencies
pip3 install -r requirements.txt --break-system-packages
```

### "externally-managed-environment" error

**Solution:**
Use the `--break-system-packages` flag when installing on macOS:
```bash
pip3 install -r requirements.txt --break-system-packages
```

Alternatively, use a virtual environment (recommended for production):
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
streamlit run src/ui/streamlit_app.py
```

## 💡 Tips for Beginners

### Getting Started

1. **Start Simple**
   - Begin with basic questions
   - Learn what fields are available
   - Understand your data structure

2. **Use Tool Call Expander**
   - Click "🔧 Executing Tools..."
   - See what the AI is doing
   - Learn which tools work best

3. **Iterate**
   - Ask follow-up questions
   - Refine based on results
   - Build on previous answers

### Sample Learning Path

**Day 1:**
```
"What fields can I query?"
"How many resources do we have?"
"Show me all unique environments"
```

**Day 2:**
```
"What's the total cost by department?"
"Show me top 5 cost centers"
"Find all production resources"
```

**Day 3:**
```
"Analyze costs by environment and department"
"Which team owns the most resources?"
"Find resources without proper tags"
```

**Week 2+:**
```
"Compare production vs staging costs"
"Identify cost optimization opportunities"
"Generate a compliance report for untagged resources"
```

## 🎓 Advanced Configuration

### Custom Models (Coming Soon)

To use local models:

1. Install LM Studio or Ollama
2. Run local model server
3. Select "Custom" provider
4. Enter API endpoint

### API Key Rotation

For security, rotate keys monthly:

```bash
# 1. Generate new key in provider dashboard
# 2. Update in application
# 3. Revoke old key
# 4. Test with new key
```

### Cost Tracking

Monitor usage:
1. OpenRouter: Check "Usage" in dashboard
2. Claude: Check "Billing" in console
3. Set up alerts for spending limits

## 📞 Getting Help

If you're stuck:

1. **Check this guide** - Most issues are covered
2. **Review error messages** - They're usually specific
3. **Check logs** - Run with `--logger.level=debug`
4. **Test components**:
   - MongoDB: `mongosh`
   - API: Try in Postman/curl
   - Tools: Run MCP server tests
5. **Open an issue** - With error messages and steps to reproduce

## 🎉 You're Ready!

Once setup is complete, you should be able to:
- ✅ Ask questions about your data
- ✅ Get AI-powered insights
- ✅ Use natural language queries
- ✅ Access all MongoDB tools
- ✅ Analyze costs and resources

**Start exploring your data with AI!** 🚀

---

**Next Steps:**
- Read [AI_QUERY_ASSISTANT.md](AI_QUERY_ASSISTANT.md) for usage guide
- Try example questions
- Explore different models
- Monitor API costs
