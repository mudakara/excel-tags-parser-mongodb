# Excel Tags Parser

A Python application with a web-based UI to process large Excel files (100,000+ rows) by parsing a "Tags" column and extracting structured information into separate columns.

## Features

- **User-friendly Web Interface** built with Streamlit
- **Handles Large Files** - Optimized to process 100,000+ rows efficiently
- **Chunked Processing** - Memory-efficient processing using pandas chunks
- **Multiple Tag Formats** - Supports various tag formats (key-value, pipe-separated, JSON)
- **Real-time Progress** - Live progress tracking during processing
- **Download Results** - Easy download of processed files
- **MongoDB Integration** - Push data to MongoDB for dashboards and analytics
- **MCP Server** - Query database and create charts using AI/LLMs
- **Command Line Interface** - CLI option for batch processing

## Extracted Information

The application reads each row in the "Tags" column and extracts:
1. **Application Name**
2. **Environment**
3. **Owner**

These values are added as new columns in the processed Excel file.

## Supported Tag Formats

### 1. Key-Value Pairs (Recommended)
```
app:myapp,env:production,owner:john.doe
application:webapp,environment:dev,owner:jane.smith
```

### 2. Pipe-Separated Values
```
myapp|production|john.doe
webapp|dev|jane.smith
```

### 3. JSON Format
```json
{"app":"myapp","env":"production","owner":"john.doe"}
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Web Interface (Recommended)

1. **Start the Streamlit application**
   ```bash
   streamlit run src/ui/streamlit_app.py
   ```

2. **Open your browser** - The app will automatically open at `http://localhost:8501`

3. **Upload your Excel file** - Click "Browse files" and select your Excel file

4. **Review the preview** - Check that the Tags column is recognized

5. **Click "Process File"** - Wait for processing to complete

6. **Download the results** - Click "Download Processed File"

7. **Push to MongoDB (Optional)** - Click "Push to MongoDB" to store data for dashboards

### MongoDB Integration

The application includes MongoDB integration for storing processed data:

1. **Install MongoDB** - See [MONGODB_SETUP.md](MONGODB_SETUP.md) for installation instructions

2. **Start MongoDB**:
   ```bash
   # macOS
   brew services start mongodb-community@7.0

   # Linux
   sudo systemctl start mongod
   ```

3. **Test Connection** - Use the "Test MongoDB Connection" button in the sidebar

4. **Push Data** - After processing, click "Push to MongoDB" button

5. **View Statistics** - See database statistics including unique applications, environments, and owners

For detailed MongoDB setup, schema design, and querying guide, see [MONGODB_SETUP.md](MONGODB_SETUP.md).

### MCP Server for AI/LLM Integration

Use AI to analyze your data! The MCP (Model Context Protocol) server allows open-source LLMs to query MongoDB and create charts:

1. **Setup MCP Server**:
   ```bash
   cd mcp_server
   pip install -r requirements.txt
   python test_mcp.py  # Verify it works
   ```

2. **Connect to an LLM** (LM Studio, Claude Desktop, Continue.dev, etc.)

3. **Ask Natural Language Questions**:
   - "Show me database statistics"
   - "Create a bar chart of resources by environment"
   - "Which owner has the most resources?"
   - "Make a heatmap of applications across environments"

See [mcp_server/QUICKSTART.md](mcp_server/QUICKSTART.md) for detailed setup instructions.

See [mcp_server/PROMPTS.md](mcp_server/PROMPTS.md) for example prompts.

### Command Line Interface

For batch processing or automation:

```bash
python src/app.py <input_file> <output_file>
```

**Example:**
```bash
python src/app.py data/uploads/myfile.xlsx data/processed/myfile_processed.xlsx
```

## Project Structure

```
excel-tags-parser/
├── src/
│   ├── app.py                 # CLI entry point
│   ├── ui/
│   │   └── streamlit_app.py   # Web UI
│   ├── processor/
│   │   ├── excel_reader.py    # Excel reading with chunking
│   │   ├── tag_parser.py      # Tag parsing logic
│   │   └── excel_writer.py    # Excel writing
│   ├── database/
│   │   ├── mongodb_client.py  # MongoDB connection
│   │   └── mongodb_operations.py  # Data insertion & queries
│   └── utils/
│       └── validators.py      # Input validation
├── mcp_server/                # MCP server for LLM integration
│   ├── mongodb_mcp_server.py  # MCP server implementation
│   ├── requirements.txt       # MCP dependencies
│   ├── QUICKSTART.md          # Quick start guide
│   ├── PROMPTS.md             # Example prompts for LLMs
│   └── test_mcp.py            # Test script
├── data/
│   ├── uploads/               # Temporary uploads (auto-cleaned)
│   └── processed/             # Processed files
├── tests/                     # Test files
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── MONGODB_SETUP.md           # MongoDB setup guide
```

## Configuration

Edit `config.py` to customize settings:

```python
# Processing settings
CHUNK_SIZE = 10000              # Rows per chunk
MAX_FILE_SIZE_MB = 500          # Maximum upload size

# Column names
TAG_COLUMN = 'Tags'             # Name of the tags column

# Tag parsing
TAG_SEPARATORS = [',', ';', '|']
KEY_VALUE_SEPARATOR = ':'

# MongoDB settings
MONGODB_URI = 'mongodb://localhost:27017/'
MONGODB_DATABASE = 'azure'
MONGODB_COLLECTION = 'resources'
```

## Customizing Tag Parsing

If your tags have a different format, modify the `parse_tags()` function in `src/processor/tag_parser.py`.

### Example: Custom Format

If your tags look like: `myapp-production-john.doe`

Add this to the `parse_tags()` function:

```python
# Strategy: Dash-separated format
elif '-' in tag_string and tag_string.count('-') >= 2:
    parts = tag_string.split('-')
    result['Application Name'] = parts[0].strip()
    result['Environment'] = parts[1].strip()
    result['Owner'] = parts[2].strip()
```

## Performance

- **100K rows**: ~30-60 seconds
- **500K rows**: ~2-4 minutes
- **1M rows**: ~5-8 minutes

Performance depends on:
- File size and complexity
- Tag format complexity
- System specifications

## Troubleshooting

### Error: "Column 'Tags' not found"
- Ensure your Excel file has a column named "Tags" (case-sensitive)
- Or modify `TAG_COLUMN` in `config.py` to match your column name

### Error: "File size exceeds maximum"
- Increase `MAX_FILE_SIZE_MB` in `config.py`

### Memory Issues
- Reduce `CHUNK_SIZE` in `config.py` (e.g., from 10000 to 5000)

### Slow Processing
- Increase `CHUNK_SIZE` for faster processing (uses more memory)
- Enable parallel processing: Set `ENABLE_PARALLEL_PROCESSING = True` in `config.py`

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Tag Formats

1. Edit `src/processor/tag_parser.py`
2. Add a new parsing function (e.g., `_parse_custom_format()`)
3. Call it from `parse_tags()` based on detection logic
4. Test with sample data

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Requirements

- pandas >= 2.0.0
- openpyxl >= 3.1.0
- xlrd >= 2.0.0
- streamlit >= 1.28.0
- python-dotenv >= 1.0.0
- pymongo >= 4.6.0 (for MongoDB integration)

## License

This project is provided as-is for internal use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs in the console
3. Check the sample files in `data/` directory

## Example Workflow

1. **Prepare your Excel file**
   - Ensure it has a "Tags" column
   - Tags should follow one of the supported formats

2. **Run the application**
   ```bash
   streamlit run src/ui/streamlit_app.py
   ```

3. **Upload and process**
   - Upload your file
   - Click "Process File"
   - Wait for completion

4. **Review results**
   - Check the statistics
   - Preview the parsed data
   - Download the processed file

5. **Push to MongoDB (Optional)**
   - Click "Push to MongoDB" button
   - View database statistics
   - Create dashboards using the stored data

6. **Verify output**
   - Open the downloaded file
   - Check the three new columns: Application Name, Environment, Owner

## Advanced Usage

### Programmatic Usage

```python
from src.processor.excel_reader import read_excel_in_chunks
from src.processor.tag_parser import process_dataframe
from src.processor.excel_writer import write_chunks_to_excel

# Process file
processed_chunks = []
for chunk, total in read_excel_in_chunks('input.xlsx'):
    processed_chunk = process_dataframe(chunk)
    processed_chunks.append(processed_chunk)

# Save results
write_chunks_to_excel(processed_chunks, 'output.xlsx')
```

### Batch Processing Multiple Files

```bash
for file in data/uploads/*.xlsx; do
    python src/app.py "$file" "data/processed/$(basename "$file" .xlsx)_processed.xlsx"
done
```

## Notes

- Processed files are saved in `data/processed/` directory
- Uploaded files are temporarily stored and auto-cleaned after processing
- All timestamps in output filenames use format: YYYYMMDD_HHMMSS
- Empty or malformed tags will result in NULL values in the new columns
