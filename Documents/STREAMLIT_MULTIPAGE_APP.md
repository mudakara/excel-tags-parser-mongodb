# Streamlit Multi-Page Application Guide

## 🎯 Overview

The Excel Tags Parser application now has a **3-page structure** for better organization and user experience:

1. **🏠 Home** - Landing page with overview, stats, and quick actions
2. **📤 Excel Upload** - Upload and process Excel files with tag parsing
3. **📊 Reports** - Query, analyze, and visualize MongoDB data

## 📁 Project Structure

```
src/ui/
├── streamlit_app.py              # Home page (main entry point)
└── pages/
    ├── 1_📤_Excel_Upload.py      # Excel upload and processing
    └── 2_📊_Reports.py            # Data reports and analytics
```

## 🚀 Running the Application

### 1. Start MongoDB

```bash
# macOS (Homebrew)
brew services start mongodb-community

# Or run directly
mongod
```

### 2. Run the Streamlit App

```bash
cd /Users/davisgeorge/Documents/Claude/infra
streamlit run src/ui/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 📄 Page Details

### 🏠 Home Page (`streamlit_app.py`)

**Purpose:** Welcome page and application hub

**Features:**
- Welcome message and overview
- Quick statistics from MongoDB
- MongoDB connection status
- Getting started guide with tabs:
  - Upload Data guide
  - View Reports guide
  - Setup instructions
- Feature highlights
- Documentation links
- Quick action buttons to navigate to other pages

**Key Functions:**
- `main()` - Main home page function
- Shows real-time MongoDB stats
- Navigation buttons to other pages

---

### 📤 Excel Upload Page (`pages/1_📤_Excel_Upload.py`)

**Purpose:** Upload and process Excel files

**Features:**
- File upload with validation
- File preview (first 5 rows)
- Tags column validation
- Progress tracking during processing
- Excel file generation with all extracted fields
- MongoDB push functionality
- Download processed Excel file
- Processing statistics display

**Key Functions:**
- `main()` - Main upload page function
- `process_file()` - Process uploaded Excel file
- `push_to_mongodb()` - Insert data into MongoDB

**Workflow:**
1. Upload Excel file
2. Validate file structure and Tags column
3. Process file (extract all tag fields)
4. Download processed Excel file
5. Optionally push to MongoDB

---

### 📊 Reports Page (`pages/2_📊_Reports.py`)

**Purpose:** Query and analyze MongoDB data

**Features:**

**Tab 1: 🔎 Query Builder**
- Build custom queries with any field combination
- Add multiple filters dynamically
- View results in table format
- Export results to CSV

**Tab 2: 📈 Aggregations**
- Count and group data by any field
- View results as table and bar chart
- Analyze distribution patterns

**Tab 3: 💰 Cost Analysis**
- Analyze costs by any dimension
- See total, average, min, max costs
- Percentage breakdown
- Visualize with bar and pie charts
- Optional filtering before grouping

**Tab 4: 📊 Visualizations**
- Create bar charts
- Create pie charts
- Trend analysis (for time-series data)

**Key Functions:**
- `main()` - Main reports page function
- `get_available_fields()` - Get all queryable fields
- `advanced_query()` - Query with any filters
- `aggregate_by_field()` - Group and count by field
- `cost_analysis_by_field()` - Cost breakdown by field

---

## 🎨 Navigation

### Sidebar Navigation

Streamlit automatically creates sidebar navigation for all pages:

```
🏠 streamlit_app
📤 Excel Upload
📊 Reports
```

Users can click on any page to navigate.

### Programmatic Navigation

Use `st.switch_page()` for button navigation:

```python
# Navigate to Excel Upload
if st.button("📤 Upload Excel File"):
    st.switch_page("pages/1_📤_Excel_Upload.py")

# Navigate to Reports
if st.button("📊 View Reports"):
    st.switch_page("pages/2_📊_Reports.py")
```

## 🔧 Session State

The application uses Streamlit session state to share data between pages:

```python
# Excel Upload page stores processed data
st.session_state['processed_df'] = final_df
st.session_state['processed_filename'] = original_filename
st.session_state['processing_complete'] = True

# Other pages can access this data
if st.session_state.processed_df is not None:
    # Use the data
    pass
```

## 🎯 Key Features

### 1. Dynamic Field Support

All pages support dynamically extracted fields:
- Home page shows overview
- Excel Upload extracts all fields
- Reports page queries any field

### 2. Real-Time Stats

Home page shows real-time MongoDB statistics:
- Total documents
- Unique applications
- Unique environments
- Unique owners

### 3. Progress Tracking

Excel Upload page shows:
- Processing progress bar
- Chunk processing status
- Excel writing progress
- MongoDB insertion progress

### 4. Interactive Visualizations

Reports page uses Plotly for:
- Interactive bar charts
- Interactive pie charts
- Hover tooltips
- Zoom and pan

### 5. Export Capabilities

- Download processed Excel files
- Export query results to CSV
- Download visualizations (built-in Plotly feature)

## 📊 Data Flow

```
1. User uploads Excel file
   ↓
2. Excel Upload page processes file
   ↓
3. Extracted data → MongoDB
   ↓
4. Reports page queries MongoDB
   ↓
5. User views analytics and visualizations
```

## 🛠️ Customization

### Adding a New Page

1. Create a new file in `src/ui/pages/`:
   ```python
   # pages/3_🔧_Settings.py
   import streamlit as st

   st.set_page_config(page_title="Settings", page_icon="🔧")

   def main():
       st.title("🔧 Settings")
       # Your page content

   if __name__ == "__main__":
       main()
   ```

2. Streamlit automatically detects and adds it to navigation!

### Customizing Page Order

Use number prefixes:
- `1_` - First page
- `2_` - Second page
- `3_` - Third page

### Changing Page Icons

Edit the filename:
- `1_📤_Excel_Upload.py` → Excel icon
- `2_📊_Reports.py` → Chart icon
- `3_🔧_Settings.py` → Gear icon

## 🐛 Troubleshooting

### Issue: Pages not showing in sidebar

**Solution:** Make sure page files are in the `pages/` directory

### Issue: Import errors in pages

**Solution:** Add path configuration at top of each page:
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
```

### Issue: Session state not persisting

**Solution:** Use `st.session_state` dictionary, not regular variables

### Issue: MongoDB connection error

**Solution:** Ensure MongoDB is running:
```bash
brew services start mongodb-community
```

## 📚 Best Practices

### 1. Page Configuration

Always set page config at the top of each page:
```python
st.set_page_config(
    page_title="Your Page Title",
    page_icon="🎯",
    layout="wide"
)
```

### 2. Logging

Use Python logging instead of print:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Processing started")
```

### 3. Error Handling

Always use try-except for MongoDB operations:
```python
try:
    stats = get_statistics()
except Exception as e:
    logger.error(f"Error getting stats: {e}")
    st.error("Could not load statistics")
```

### 4. User Feedback

Provide clear feedback:
```python
with st.spinner("Processing..."):
    # Long operation
    pass

st.success("✅ Processing complete!")
```

## 🎉 Benefits of Multi-Page Structure

✅ **Better Organization** - Logical separation of concerns
✅ **Cleaner Code** - Each page is self-contained
✅ **Better UX** - Clear navigation and focus
✅ **Scalability** - Easy to add new pages
✅ **Maintainability** - Easier to update individual pages

## 🔗 Related Documentation

- [Streamlit Multi-Page Apps](https://docs.streamlit.io/library/get-started/multipage-apps)
- [DYNAMIC_PARSING_GUIDE.md](DYNAMIC_PARSING_GUIDE.md) - Tag parsing details
- [MCP_DYNAMIC_QUERY_TOOLS.md](MCP_DYNAMIC_QUERY_TOOLS.md) - MCP tools for querying

---

**Happy analyzing!** 🚀
