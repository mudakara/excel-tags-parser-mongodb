# Excel Tags Parser - Project Context

## Project Overview
A Python application with a user interface to upload and process large Excel files (100,000+ rows) by parsing a "Tags" column and extracting structured information into separate columns.

## Business Requirements

### Functional Requirements
1. **File Upload Interface**
   - User-friendly UI to upload Excel files (.xlsx, .xls)
   - File validation and error handling
   - Progress indication during processing

2. **Data Processing**
   - Read Excel files with 100,000+ rows efficiently
   - Parse the "Tags" column in each row
   - Extract three pieces of information:
     - Application Name
     - Environment
     - Owner
   - Create three new columns with extracted data
   - Export processed data back to Excel

3. **Performance Requirements**
   - Handle files with 1 lakh (100,000+) rows
   - Optimize memory usage
   - Process data in chunks to avoid memory overflow
   - Provide real-time progress feedback

### Non-Functional Requirements
- Response time: Process 100K rows in under 2 minutes
- Memory efficient: Use streaming/chunked processing
- Error resilient: Handle malformed data gracefully
- User-friendly: Clear error messages and progress indicators

## Technical Stack

### Core Technologies
- **Python 3.9+**
- **pandas**: Efficient data manipulation with chunking support
- **openpyxl**: Excel file reading/writing (.xlsx)
- **xlrd**: Legacy Excel support (.xls)

### UI Framework Options
Choose one based on requirements:

1. **Streamlit** (Recommended)
   - Fast development
   - Built-in file uploader
   - Easy deployment
   - Real-time progress bars

2. **Flask + HTML/CSS/JS**
   - More control over UI
   - Better for production deployment
   - Requires more frontend work

3. **PyQt/Tkinter**
   - Desktop application
   - No web server needed
   - Native OS integration

## Architecture

### Component Structure
```
excel-tags-parser/
├── src/
│   ├── __init__.py
│   ├── app.py                 # Main application entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   └── streamlit_app.py   # UI implementation
│   ├── processor/
│   │   ├── __init__.py
│   │   ├── excel_reader.py    # Excel file reading
│   │   ├── tag_parser.py      # Tag parsing logic
│   │   └── excel_writer.py    # Excel file writing
│   └── utils/
│       ├── __init__.py
│       └── validators.py      # Input validation
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   └── test_processor.py
├── data/
│   ├── uploads/               # Temporary upload storage
│   └── processed/             # Processed file output
├── requirements.txt
├── README.md
└── config.py                  # Configuration settings
```

## Key Implementation Details

### 1. Excel Reading Strategy
```python
# Use chunked reading for large files
import pandas as pd

def read_excel_in_chunks(file_path, chunk_size=10000):
    """
    Read Excel file in chunks to optimize memory usage
    """
    excel_file = pd.ExcelFile(file_path)
    total_rows = excel_file.book.worksheets[0].max_row

    for chunk in pd.read_excel(
        file_path,
        chunksize=chunk_size,
        engine='openpyxl'
    ):
        yield chunk, total_rows
```

### 2. Tag Parsing Logic

**Expected Tag Format Examples:**
- `app:myapp,env:production,owner:john.doe`
- `application:webapp|environment:dev|owner:jane.smith`
- `myapp-production-john` (pattern-based)

**Parser Implementation Strategy:**
```python
import re

def parse_tags(tag_string):
    """
    Parse tags column and extract application, environment, owner

    Supports multiple formats:
    1. Key-value pairs: "app:myapp,env:prod,owner:john"
    2. Pipe-separated: "myapp|prod|john"
    3. Pattern-based: "myapp-prod-john"
    """
    result = {
        'Application Name': None,
        'Environment': None,
        'Owner': None
    }

    if pd.isna(tag_string):
        return result

    tag_string = str(tag_string).strip()

    # Strategy 1: Key-value pairs (comma or semicolon separated)
    if ':' in tag_string:
        pairs = re.split(r'[,;|]', tag_string)
        for pair in pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if key in ['app', 'application', 'application_name']:
                    result['Application Name'] = value
                elif key in ['env', 'environment']:
                    result['Environment'] = value
                elif key in ['owner', 'owner_name']:
                    result['Owner'] = value

    # Strategy 2: Pipe-separated values (assumed order)
    elif '|' in tag_string:
        parts = tag_string.split('|')
        if len(parts) >= 3:
            result['Application Name'] = parts[0].strip()
            result['Environment'] = parts[1].strip()
            result['Owner'] = parts[2].strip()

    # Strategy 3: Pattern matching (customize based on actual data)
    else:
        # Add custom pattern matching logic based on your data format
        pass

    return result
```

### 3. Processing Pipeline
```python
def process_excel_file(input_path, output_path, progress_callback=None):
    """
    Main processing function with progress tracking
    """
    chunk_size = 10000
    processed_chunks = []
    total_processed = 0

    for chunk, total_rows in read_excel_in_chunks(input_path, chunk_size):
        # Parse tags for each row in chunk
        parsed_data = chunk['Tags'].apply(parse_tags)

        # Convert parsed data to DataFrame
        parsed_df = pd.DataFrame(parsed_data.tolist())

        # Combine with original data
        result_chunk = pd.concat([chunk, parsed_df], axis=1)
        processed_chunks.append(result_chunk)

        # Update progress
        total_processed += len(chunk)
        if progress_callback:
            progress_callback(total_processed, total_rows)

    # Combine all chunks
    final_df = pd.concat(processed_chunks, ignore_index=True)

    # Write to Excel
    final_df.to_excel(output_path, index=False, engine='openpyxl')

    return final_df
```

### 4. Streamlit UI Implementation
```python
import streamlit as st
import os
from datetime import datetime

def main():
    st.title("Excel Tags Parser")
    st.write("Upload an Excel file to extract Application Name, Environment, and Owner from Tags column")

    # File upload
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls']
    )

    if uploaded_file is not None:
        # Save uploaded file
        upload_path = f"data/uploads/{uploaded_file.name}"
        with open(upload_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"File uploaded: {uploaded_file.name}")

        # Process button
        if st.button("Process File"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(processed, total):
                progress = int((processed / total) * 100)
                progress_bar.progress(progress)
                status_text.text(f"Processing: {processed:,} / {total:,} rows ({progress}%)")

            try:
                # Process file
                output_filename = f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                output_path = f"data/processed/{output_filename}"

                result_df = process_excel_file(
                    upload_path,
                    output_path,
                    update_progress
                )

                st.success("Processing complete!")

                # Show preview
                st.subheader("Preview (first 100 rows)")
                st.dataframe(result_df.head(100))

                # Download button
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="Download Processed File",
                        data=f,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

            finally:
                # Cleanup uploaded file
                if os.path.exists(upload_path):
                    os.remove(upload_path)
```

## Performance Optimizations

### Memory Management
1. **Chunked Processing**: Read and process data in chunks of 10,000 rows
2. **Generator Pattern**: Use generators to avoid loading entire file into memory
3. **Garbage Collection**: Explicitly clear large objects after processing

### Speed Optimizations
1. **Vectorized Operations**: Use pandas vectorized operations instead of loops
2. **Compiled Regex**: Pre-compile regex patterns for tag parsing
3. **Parallel Processing**: Use multiprocessing for independent chunk processing
4. **Engine Selection**: Use 'openpyxl' for .xlsx (faster than xlrd)

### Example: Parallel Processing
```python
from multiprocessing import Pool
import pandas as pd

def process_chunk_parallel(chunk):
    parsed_data = chunk['Tags'].apply(parse_tags)
    parsed_df = pd.DataFrame(parsed_data.tolist())
    return pd.concat([chunk, parsed_df], axis=1)

def process_excel_parallel(input_path, output_path, num_workers=4):
    chunks = list(read_excel_in_chunks(input_path))

    with Pool(num_workers) as pool:
        processed_chunks = pool.map(process_chunk_parallel, chunks)

    final_df = pd.concat(processed_chunks, ignore_index=True)
    final_df.to_excel(output_path, index=False)
    return final_df
```

## Configuration File (config.py)
```python
import os

# Application settings
CHUNK_SIZE = 10000  # Rows per chunk
MAX_FILE_SIZE_MB = 500  # Maximum upload file size
ALLOWED_EXTENSIONS = ['.xlsx', '.xls']

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'data', 'uploads')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Tag parsing patterns
TAG_SEPARATORS = [',', ';', '|']
KEY_VALUE_SEPARATOR = ':'

# Column names
TAG_COLUMN = 'Tags'
NEW_COLUMNS = ['Application Name', 'Environment', 'Owner']
```

## Dependencies (requirements.txt)
```
pandas>=2.0.0
openpyxl>=3.1.0
xlrd>=2.0.0
streamlit>=1.28.0
python-dotenv>=1.0.0
```

## Testing Strategy

### Unit Tests
- Test tag parsing with various formats
- Test chunk reading functionality
- Test data validation

### Integration Tests
- Test end-to-end processing with sample files
- Test error handling with malformed data
- Test progress callback functionality

### Performance Tests
- Benchmark with 100K, 500K, 1M rows
- Memory profiling during processing
- Speed optimization validation

## Error Handling

### Common Scenarios
1. **Missing Tags Column**: Validate column exists before processing
2. **Empty Tags**: Return None values for empty tags
3. **Malformed Tags**: Log errors and continue processing
4. **File Corruption**: Validate file integrity before processing
5. **Memory Errors**: Reduce chunk size dynamically

## Deployment

### Local Development
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run src/ui/streamlit_app.py
```

### Production Deployment Options
1. **Streamlit Cloud**: Free hosting for Streamlit apps
2. **Docker Container**: Containerize for consistent deployment
3. **AWS/Azure/GCP**: Deploy on cloud platforms

## Future Enhancements
1. Support for CSV files
2. Custom tag format configuration via UI
3. Batch processing multiple files
4. Export to multiple formats (CSV, JSON)
5. Data validation rules
6. Audit logging and processing history
7. API endpoint for programmatic access

## Notes on Tag Format
**IMPORTANT**: The current implementation assumes certain tag formats. You need to:
1. Analyze actual tag data format from sample Excel files
2. Customize the `parse_tags()` function accordingly
3. Add validation rules specific to your data

**Example tag formats to support:**
- `app:myapp,env:production,owner:john.doe`
- `application=myapp;environment=prod;owner=john`
- JSON format: `{"app": "myapp", "env": "prod", "owner": "john"}`

Update the parser based on your actual data structure.
