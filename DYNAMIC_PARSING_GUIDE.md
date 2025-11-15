# Dynamic Tag Parsing Guide

## 🎯 Overview

The tag parser has been **completely rewritten** to extract **ALL key-value pairs** from the Tags column dynamically, instead of only extracting predefined fields.

### Before (Old Behavior) ❌
- Only extracted: Application Name, Environment, Owner, Cost
- Ignored all other fields in tags
- Fixed columns only

### After (New Behavior) ✅
- Extracts **ALL** key-value pairs found in tags
- Creates a column for each unique key
- Dynamic columns based on your data
- Properly formatted column names

---

## 📝 How It Works

### Example 1: Custom Fields

**Tags Input:**
```
"primarycontact":"midhun jose","usage":"databricks prod env, hot storage"
```

**Output Columns Created:**
- `Primary Contact` → "midhun jose"
- `Usage` → "databricks prod env, hot storage"

### Example 2: Standard + Custom Fields

**Tags Input:**
```
"owner":"john","environment":"production","primarycontact":"jane doe","costcenter":"CC123"
```

**Output Columns Created:**
- `Owner` → "john"
- `Environment` → "production"
- `Primary Contact` → "jane doe"
- `Cost Center` → "CC123"

### Example 3: All Custom Fields

**Tags Input:**
```
"department":"IT","project":"analytics","team":"data","businessunit":"corporate"
```

**Output Columns Created:**
- `Department` → "IT"
- `Project` → "analytics"
- `Team` → "data"
- `Business Unit` → "corporate"

---

## 🔧 Supported Tag Formats

### 1. Escaped JSON Format ✅
```
"key1":"value1","key2":"value2","key3":"value3"
```

**Example:**
```
"owner":"john","primarycontact":"jane","usage":"databricks"
```

### 2. Key-Value Pairs ✅
```
key1:value1,key2:value2,key3:value3
```

**Example:**
```
applicationname:myapp,environment:prod,team:analytics,usage:databricks
```

### 3. JSON Format ✅
```json
{"key1": "value1", "key2": "value2", "key3": "value3"}
```

**Example:**
```json
{"owner": "john", "primarycontact": "jane", "department": "IT"}
```

### 4. Pipe-Separated (Limited) ⚠️
```
value1|value2|value3|value4
```

**Note:** Pipe-separated format uses predefined field order:
- Position 1: Application Name
- Position 2: Environment
- Position 3: Owner
- Position 4: Cost

---

## 📐 Column Name Formatting

The parser automatically formats tag keys into proper column names:

| Tag Key | Column Name |
|---------|-------------|
| `primarycontact` | Primary Contact |
| `application_name` | Application Name |
| `applicationname` | Application Name |
| `costcenter` | Cost Center |
| `cost_center` | Cost Center |
| `businessunit` | Business Unit |
| `business_unit` | Business Unit |
| `department` | Department |
| `project` | Project |
| `team` | Team |
| `usage` | Usage |
| `custom_field` | Custom Field |

**Rules:**
1. Special cases are handled (e.g., "primarycontact" → "Primary Contact")
2. Underscores are replaced with spaces
3. Title case is applied
4. Consistent formatting across all data

---

## 🎨 Real-World Example

### Input Excel File (Tags Column)

| Row | Tags |
|-----|------|
| 1 | `"owner":"john","primarycontact":"jane","usage":"databricks prod"` |
| 2 | `"owner":"alice","department":"IT","costcenter":"CC123"` |
| 3 | `"environment":"production","team":"analytics","project":"sales"` |

### Output Excel File (After Processing)

| Row | Owner | Primary Contact | Usage | Department | Cost Center | Environment | Team | Project | Date |
|-----|-------|----------------|-------|------------|------------|-------------|------|---------|------|
| 1 | john | jane | databricks prod | | | | | | 2025-11 |
| 2 | alice | | | IT | CC123 | | | | 2025-11 |
| 3 | | | | | | production | analytics | sales | 2025-11 |

**Notes:**
- Empty cells where field wasn't present in that row's tags
- All unique keys across ALL rows become columns
- Date column added automatically from Summary sheet

---

## 💾 MongoDB Storage

All extracted fields are stored in MongoDB with the same dynamic structure:

```javascript
{
  // All extracted fields stored at top level for easy querying
  "owner": "john",
  "primaryContact": "jane",
  "usage": "databricks prod",
  "department": "IT",
  "costCenter": "CC123",
  // ... any other fields found

  "date": "2025-11",

  // Tags information
  "tags": {
    "raw": "original tag string",
    "parsed": {
      // All extracted key-value pairs
    }
  },

  // All original Excel data
  "originalData": {
    // Everything from Excel preserved
  },

  // Metadata
  "metadata": {
    "importDate": "2025-11-15T...",
    "sourceFile": "filename.xlsx",
    "dataDate": "2025-11"
  }
}
```

---

## 🔍 Handling Duplicates

If a column already exists in your Excel file and is also found in tags, the **original Excel column value is used**.

**Example:**
- Excel has column "Cost" with value 1234.56
- Tags has "cost":"100"
- **Result:** Cost column = 1234.56 (from Excel, not tags)

**Log message:**
```
Dropping duplicate columns from parsed data (keeping original): ['Cost']
```

---

## 📊 Processing Statistics

The parser logs detailed statistics about what was extracted:

```
Processing 10000 rows with date value: 2025-11
Created 15 new columns from tags: ['Owner', 'Primary Contact', 'Usage', 'Department', ...]
  - Owner: 8543 rows with data
  - Primary Contact: 6234 rows with data
  - Usage: 4521 rows with data
  - Department: 9876 rows with data
  ...
Added Date column with value: 2025-11
```

---

## 🚀 Usage in Code

### Streamlit UI
The Streamlit UI automatically uses dynamic parsing - no changes needed!

Just upload your Excel file and all fields will be extracted.

### Programmatic Usage

```python
from src.processor.tag_parser import parse_tags

# Parse a tag string
tags = '"owner":"john","primarycontact":"jane","usage":"databricks"'
result = parse_tags(tags)

print(result)
# Output: {'Owner': 'john', 'Primary Contact': 'jane', 'Usage': 'databricks'}
```

### Process a DataFrame

```python
from src.processor.tag_parser import process_dataframe
import pandas as pd

df = pd.read_excel('your_file.xlsx', sheet_name='Data')
result_df = process_dataframe(df, date_value='2025-11')

# Result has all original columns + all extracted tag columns + Date column
print(result_df.columns)
```

---

## 🎯 Benefits

✅ **Flexible**: Works with any tag structure
✅ **Automatic**: No need to predefine fields
✅ **Complete**: Extracts ALL information from tags
✅ **Clean**: Properly formatted column names
✅ **Safe**: Handles duplicates and conflicts
✅ **Fast**: Vectorized pandas operations

---

## 📈 Performance

- **Same speed** as before (vectorized operations)
- **No degradation** for large files (100K+ rows)
- **Efficient memory** usage with chunked processing

---

## 🔧 Customization

### Add Custom Field Mappings

Edit `src/processor/tag_parser.py` and update the `special_cases` dictionary in `format_column_name()`:

```python
special_cases = {
    'applicationname': 'Application Name',
    'primarycontact': 'Primary Contact',
    'myfield': 'My Custom Field',  # Add your custom mappings here
    # ... more mappings
}
```

### Skip Certain Fields

If you want to skip certain fields from being extracted, you can filter them in `parse_tags()`:

```python
# In parse_tags() function, before returning result:
skip_fields = ['internal_id', 'temp_field']
result = {k: v for k, v in result.items() if k.lower() not in skip_fields}
```

---

## 📝 Migration from Old Version

If you were relying on specific column names, make sure they match the new formatted names:

| Old Column | New Column |
|-----------|------------|
| `Application Name` | `Application Name` ✅ (same) |
| `Environment` | `Environment` ✅ (same) |
| `Owner` | `Owner` ✅ (same) |
| `Cost` | `Cost` ✅ (same) |

All custom fields will now also be extracted!

---

## 🐛 Troubleshooting

### Issue: Too many columns created

**Cause:** Tags contain many unique keys across different rows

**Solution:**
1. Filter unwanted fields in the parser
2. Clean your tags before processing
3. Use MongoDB queries to select only needed fields

### Issue: Column names not formatted correctly

**Cause:** Tag key doesn't match special cases

**Solution:**
Add your custom field to `special_cases` in `format_column_name()`

### Issue: Some fields not extracted

**Cause:** Tag format not recognized

**Solution:**
Check the tag format and verify it matches one of the supported formats. Enable debug logging to see parsing details.

---

## 📞 Support

For issues or questions:
1. Check the logs for parsing details
2. Test with `test_dynamic_parsing.py`
3. See `TROUBLESHOOTING.md` for common errors

---

**Dynamic parsing is now live!** 🎉

All fields in your tags will be automatically extracted and available for analysis.
