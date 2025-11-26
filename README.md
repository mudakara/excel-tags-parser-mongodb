# Excel Tags Parser & Analytics Platform

A comprehensive solution for parsing Excel files with tagged resources, extracting all fields dynamically, storing data in MongoDB, and performing advanced analytics with powerful visualization capabilities.

## 🎯 Overview

This application provides a complete end-to-end workflow for:
- **📤 Uploading** Excel files with tagged data
- **🔍 Parsing** ALL fields from tags dynamically (no predefined schema)
- **💾 Storing** data in MongoDB with optimized structure
- **📊 Analyzing** data with custom queries and visualizations
- **🤖 Querying** via MCP tools for AI-powered insights

## ✨ Key Features

### Dynamic Tag Parsing
- Automatically extracts **ALL** fields from tags
- No need to predefine field names
- Supports unlimited custom fields
- Works with multiple tag formats (JSON, key-value, pipe-separated)

### Multi-Page Web Interface
- **🤖 AI Assistant**: Ask questions about Azure cost and Infrastructure related data
- **📤 Excel Upload**: Upload and process large Excel files (100K+ rows)
- **🔎 Query Builder**: Build custom queries with dynamic filters and field selection
- **💰 Cost Analysis**: Analyze costs by Application, Environment, Owner, and Date range
- **📊 Drill Down Analysis**: Hierarchical cost analysis (Application → Environment → Owner)
- **📈 Monthly Comparison**: Compare monthly costs across applications
- **❓ Help**: Interactive documentation viewer with search and navigation

### MongoDB Integration
- Optimized document structure for analytics
- All dynamic fields stored at top level for easy querying
- Automatic indexing for performance
- Real-time statistics

### MCP Server
- 10+ tools for advanced data analysis
- Query by any field combination
- Cost analysis by any dimension
- Cross-tabulation and aggregations
- AI-friendly API for Claude and other LLMs

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB 4.0+
- Excel files with tagged data

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mudakara/excel-tags-parser-mongodb.git
   cd excel-tags-parser-mongodb
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Start MongoDB**
   ```bash
   # macOS (Homebrew)
   brew services start mongodb-community

   # Or run directly
   mongod
   ```

4. **Run the application**
   ```bash
   streamlit run src/ui/streamlit_app.py
   ```

5. **Open in browser**
   - The app will automatically open at `http://localhost:8501`

## 📁 Project Structure

```
excel-tags-parser-mongodb/
├── README.md                        # This file - project overview
├── Documents/                       # 📚 All documentation (26 files)
│   ├── INDEX.md                    # Documentation index with links
│   ├── 🚀 Getting Started/
│   ├── 🏗️ Core Features/
│   ├── 🔌 MCP Integration/
│   ├── 🎨 UI Components/
│   ├── ⚡ Performance Optimizations/
│   └── 🔧 Troubleshooting/
├── src/
│   ├── database/
│   │   ├── mongodb_client.py       # MongoDB connection
│   │   └── mongodb_operations.py   # CRUD operations with dynamic fields
│   ├── parser/
│   │   ├── excel_reader.py         # Excel reading with chunking
│   │   ├── excel_writer.py         # Excel writing with progress
│   │   └── tag_parser.py           # Dynamic tag parsing engine
│   ├── ui/
│   │   ├── streamlit_app.py        # Main app entry point
│   │   └── pages/
│   │       ├── 0_🏠_Home.py        # AI Assistant page
│   │       ├── 1_📤_Excel_Upload.py # Upload page
│   │       ├── 2_🔎_Query_Builder.py # Query Builder page
│   │       ├── 3_💰_Cost_Analysis.py # Cost Analysis page
│   │       ├── 4_📊_Drill_Down_Analysis.py # Drill-down page
│   │       ├── 5_📈_Monthly_Comparison.py  # Comparison page
│   │       └── 6_❓_Help.py        # Help & Documentation page
│   └── utils/
│       └── validators.py           # File and data validation
├── mcp_server/
│   ├── server.py                   # MCP server with 10+ tools
│   └── test_mcp.py                 # MCP server tests
├── config.py                       # Configuration settings
└── requirements.txt                # Python dependencies
```

## 📖 Documentation

**📚 [Complete Documentation Index](./Documents/INDEX.md)** - All documentation organized and searchable

### Quick Links

#### Getting Started (Start Here!)
- **[Documents/MONGODB_SETUP.md](./Documents/MONGODB_SETUP.md)** - MongoDB installation and setup
- **[Documents/PROJECT_CONTEXT.md](./Documents/PROJECT_CONTEXT.md)** - Complete project overview
- **[Documents/IMPLEMENTATION_SUMMARY.md](./Documents/IMPLEMENTATION_SUMMARY.md)** - Implementation summary

#### User Guides
- **[Documents/SETUP_AI_ASSISTANT.md](./Documents/SETUP_AI_ASSISTANT.md)** - 🆕 AI assistant setup (5 min quick start)
- **[Documents/AI_QUERY_ASSISTANT.md](./Documents/AI_QUERY_ASSISTANT.md)** - 🆕 AI query guide with examples
- **[Documents/STREAMLIT_MULTIPAGE_APP.md](./Documents/STREAMLIT_MULTIPAGE_APP.md)** - Multi-page app guide
- **[Documents/DYNAMIC_PARSING_GUIDE.md](./Documents/DYNAMIC_PARSING_GUIDE.md)** - How dynamic tag parsing works
- **[Documents/MCP_QUICKSTART.md](./Documents/MCP_QUICKSTART.md)** - Quick start for MCP tools

#### Technical Documentation
- **[Documents/MONGODB_DYNAMIC_FIELDS_UPDATE.md](./Documents/MONGODB_DYNAMIC_FIELDS_UPDATE.md)** - MongoDB schema and dynamic fields
- **[Documents/MCP_DYNAMIC_QUERY_TOOLS.md](./Documents/MCP_DYNAMIC_QUERY_TOOLS.md)** - Complete MCP tools reference
- **[Documents/GITHUB_SETUP.md](./Documents/GITHUB_SETUP.md)** - Repository setup guide

#### Performance Optimizations ⚡
- **[Documents/MONTHLY_COMPARISON_PAGE_OPTIMIZATION.md](./Documents/MONTHLY_COMPARISON_PAGE_OPTIMIZATION.md)** - 10-100x faster (Nov 17, 2025)
- **[Documents/DRILL_DOWN_ANALYSIS_PAGE_OPTIMIZATION.md](./Documents/DRILL_DOWN_ANALYSIS_PAGE_OPTIMIZATION.md)** - 20-30x faster (Nov 18, 2025)
- **[Documents/REPORTS_PAGE_PERFORMANCE_OPTIMIZATION.md](./Documents/REPORTS_PAGE_PERFORMANCE_OPTIMIZATION.md)** - Query optimization

#### Troubleshooting
- **[Documents/TROUBLESHOOTING.md](./Documents/TROUBLESHOOTING.md)** - General troubleshooting guide
- **[Documents/INDEX.md](./Documents/INDEX.md)** - Find specific fix documents

### Testing
- **test_dynamic_parsing.py** - Tag parsing validation
- **test_dynamic_mongodb.py** - MongoDB field insertion tests
- **test_mcp.py** - MCP server tests

**💡 Tip:** See [Documents/INDEX.md](./Documents/INDEX.md) for the complete organized documentation with 26 files categorized by topic.

## 🎨 Application Pages

### 🤖 AI Assistant
- **Natural Language Queries**: Ask questions about Azure cost and Infrastructure related data
- **Multiple LLM Support**: OpenRouter (20+ models), Claude, or custom LLMs
- **Automatic Tool Use**: AI intelligently uses MongoDB MCP tools
- **Interactive Chat**: ChatGPT-style interface with message history
- **Transparent Operations**: See which tools the AI uses
- **Real-time Analysis**: Get insights, aggregations, and cost breakdowns
- **Persistent Settings**: LLM configuration saved to MongoDB, survives page refreshes

**Example Questions:**
- "What's the total cost by department?"
- "Show me all IT resources in production"
- "Which cost center has the highest spend?"
- "Find resources without proper tags"

See [Documents/AI_QUERY_ASSISTANT.md](./Documents/AI_QUERY_ASSISTANT.md) and [Documents/SETUP_AI_ASSISTANT.md](./Documents/SETUP_AI_ASSISTANT.md) for details.

### 📤 Excel Upload Page
- File upload with validation
- Progress tracking during processing
- Extract ALL tag fields dynamically
- Download processed Excel file
- Push data to MongoDB with progress bar

### 🔎 Query Builder Page
- Build custom queries with any field combination
- Add multiple filters dynamically
- Dynamic field explorer in sidebar
- Performance optimization tools (indexing)
- Database statistics on demand
- Export results to CSV
- Cache management

### 💰 Cost Analysis Page
- Analyze costs by Application, Environment, Owner
- Single Month or Month Range selection
- Multi-select filters with $in operator support
- Total, average, min, max cost breakdown
- Monthly cost trend visualization
- Bar and pie chart visualizations
- Execution time tracking
- MongoDB query details display

### 📊 Drill Down Analysis Page
- **Hierarchical Navigation**: Application → Environment → Owner
- **Interactive Charts**: Click-based drill-down with Plotly
- **Time Period Filter**: Last 3/6/9/12 months
- **Top N Filter**: View All or Top 5/10 applications
- **Lazy Loading**: On-demand data loading (20-30x faster)
- **Caching**: 5-minute intelligent caching
- **Download**: Export owner cost data to CSV

### 📈 Monthly Comparison Page
- **Multi-Application Analysis**: Compare 1-5 applications
- **Custom Date Range**: Select any month range
- **Form-Based Input**: Optimized for no-lag configuration
- **Line Chart**: Monthly cost trends visualization
- **Pivot Table**: Monthly breakdown by application
- **Summary Metrics**: Total, average, and month count
- **Download**: Export comparison data to CSV
- **Ultra-Fast**: 10-100x faster with distinct() query optimization

### ❓ Help & Documentation Page
- **Interactive Viewer**: Read all 28 documentation files in-app
- **Categorized Sidebar**: Quick access to docs by category
- **Search Functionality**: Find specific topics and keywords
- **Navigation**: Back/Home buttons with history tracking
- **Download**: Export any document as .md file
- **No External Links**: Everything accessible within the app

See [Documents/HELP_PAGE_IMPLEMENTATION.md](./Documents/HELP_PAGE_IMPLEMENTATION.md) for details.

## 🤖 MCP Server Tools

The MCP server provides 10+ tools for advanced data analysis:

| Tool | Description |
|------|-------------|
| `get_available_fields` | List all queryable fields |
| `advanced_query` | Query by any field combination |
| `aggregate_by_any_field` | Group and aggregate by any field |
| `cost_analysis_by_field` | Cost breakdown by dimension |
| `multi_dimensional_analysis` | Cross-tabulate two fields |
| `query_resources` | Basic resource queries |
| `get_statistics` | Database overview stats |
| `get_total_cost` | Total cost with filters |
| `create_bar_chart` | Generate bar charts |
| `create_pie_chart` | Generate pie charts |

**Start MCP Server:**
```bash
cd mcp_server
python3 mongodb_mcp_server.py
```

See [MCP_QUICKSTART.md](MCP_QUICKSTART.md) for usage examples.

## 💡 Usage Examples

### Upload and Process Excel File

1. Navigate to **📤 Excel Upload** page
2. Upload your Excel file
3. The parser extracts ALL fields from tags automatically
4. Download the processed file or push to MongoDB

### Query Data

1. Navigate to **🔎 Query Builder** page
2. Add filters (e.g., `department = "IT"`, `environment = "production"`)
3. Run query and export results

### Cost Analysis

1. Navigate to **💰 Cost Analysis** page
2. Select Application, Environment, Owner filters (multi-select supported)
3. Choose Single Month or Month Range
4. Click "Calculate Total Cost"
5. View detailed breakdown with charts and metrics

### Drill Down Analysis

1. Navigate to **📊 Drill Down Analysis** page
2. Select time period (Last 3/6/9/12 months or All)
3. Choose Top N applications or view all
4. Click on application to drill into environments
5. Click on environment to see owner breakdown

## 🔧 Configuration

Edit `config.py` to customize:

```python
# MongoDB Settings
MONGODB_URI = "mongodb://localhost:27017/"
MONGODB_DATABASE = "azure"
MONGODB_COLLECTION = "resources"

# File Processing
CHUNK_SIZE = 10000
MAX_FILE_SIZE_MB = 100
ALLOWED_EXTENSIONS = ['.xlsx', '.xls']

# Tag Column
TAG_COLUMN = "Tags"
```

## 📊 Supported Tag Formats

### 1. Escaped JSON (Recommended)
```
"primarycontact":"john doe","usage":"databricks prod","department":"IT"
```

### 2. Key-Value Pairs
```
applicationname:myapp,environment:prod,owner:john,usage:databricks
```

### 3. JSON Format
```json
{"owner": "john", "environment": "production", "department": "IT"}
```

### 4. Pipe-Separated (Limited)
```
myapp|production|john|1234.56
```

## 🗃️ MongoDB Document Structure

```javascript
{
  // Standard fields
  "applicationName": "myapp",
  "environment": "production",
  "owner": "john",
  "cost": 1234.56,
  "date": "2025-11",

  // ALL dynamic fields extracted from tags
  "primaryContact": "jane doe",
  "usage": "databricks prod",
  "department": "IT",
  "costCenter": "CC123",
  "team": "analytics",
  // ... unlimited custom fields

  // Tags metadata
  "tags": {
    "raw": "original tag string",
    "parsed": { /* all extracted fields */ }
  },

  // Original Excel data
  "originalData": { /* complete row data */ },

  // Import metadata
  "metadata": {
    "importDate": "2025-11-15T...",
    "sourceFile": "filename.xlsx",
    "dataDate": "2025-11"
  }
}
```

## 🎯 Use Cases

### IT Asset Management
- Track all infrastructure resources
- Analyze costs by department, team, or owner
- Identify unused resources

### Cloud Cost Optimization
- Analyze cloud spending by dimension
- Identify cost drivers
- Track usage patterns

### Resource Governance
- Ensure proper tagging compliance
- Identify untagged or mis-tagged resources
- Generate compliance reports

### Data Analysis
- Slice and dice by any dimension
- Create custom reports
- Export data for further analysis

## 🐛 Troubleshooting

### MongoDB Connection Error
```bash
# Make sure MongoDB is running
brew services start mongodb-community

# Or
mongod
```

### Import Errors
```bash
# Reinstall dependencies
pip3 install -r requirements.txt
```

### Large File Processing
- Increase `CHUNK_SIZE` in config.py
- Ensure sufficient RAM
- Process files in batches

### Tag Parsing Issues
- Check tag format matches supported formats
- Enable debug logging in config.py
- Run test_dynamic_parsing.py to validate

## 🚀 Performance

- **Large File Support**: Handles 100K+ rows efficiently
- **Chunked Processing**: Memory-efficient streaming
- **MongoDB Indexing**: Optimized query performance
- **Batch Insertion**: Fast data loading
- **Progress Tracking**: Real-time updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

This project is open source and available under the MIT License.

## 🔗 Links

- **Repository**: https://github.com/mudakara/excel-tags-parser-mongodb
- **Issues**: https://github.com/mudakara/excel-tags-parser-mongodb/issues
- **Streamlit Docs**: https://docs.streamlit.io
- **MongoDB Docs**: https://docs.mongodb.com

## 🎉 Success Stories

- ✅ Processed 200K+ rows in under 2 minutes
- ✅ Extracted 50+ unique dynamic fields automatically
- ✅ Reduced manual tagging analysis from hours to seconds
- ✅ Enabled AI-powered querying via MCP tools

## 📞 Support

For help:
1. Check documentation in this README
2. Review troubleshooting section
3. Open an issue on GitHub

---

**Built with ❤️ using Streamlit, MongoDB, and Python**
