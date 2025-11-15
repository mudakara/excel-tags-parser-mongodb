# Troubleshooting Guide

## Error: "Column 'Tags' is completely empty"

### What This Error Means

This error occurs when the validation logic checks the Tags column and finds that it's completely empty across all rows checked. Previously, it would fail after checking just 5-10 rows, even if data existed in later rows.

### What Was Fixed

**Problem**: The old validation checked only the first 5 rows (preview), so if those rows had empty Tags, it would fail immediately.

**Solution**: Updated to read up to 10,000 rows (or entire file if smaller) before deciding if Tags column is empty.

**In `validators.py`:**

Added new function `validate_tag_column_in_file()` that:
- Reads a large sample (10,000 rows) or entire file
- Counts how many rows have data in Tags column
- Only fails if **ALL** rows are empty
- Shows helpful statistics (e.g., "5000/10000 rows have data")

**In `streamlit_app.py`:**

```python
# OLD - checked only 5 rows
preview_df = pd.read_excel(upload_path, nrows=5)
validate_tag_column(preview_df)  # Failed if first 5 rows empty

# NEW - checks up to 10,000 rows
validate_tag_column_in_file(
    upload_path,
    sheet_name='Data',
    sample_size=10000  # Reads 10k rows before deciding
)
```

### What Happens Now

1. **Preview Check**: Verifies Tags column exists (checks first 5 rows)
2. **Full Validation**: Reads up to 10,000 rows to count non-empty Tags
3. **Statistics Display**: Shows how many rows have data
4. **Smart Failure**: Only fails if ALL checked rows are empty

### Example Output

✅ **Success Case**:
```
✅ Tags column validated: 8,543/10,000 rows (85.4%) have data
```

❌ **Failure Case**:
```
❌ Column 'Tags' is completely empty (checked 10,000 rows)
```

⚠️ **Warning Case** (mostly empty but some data exists):
```
⚠️ Column 'Tags' is 92.5% empty (9,250/10,000 rows)
✅ Tags column validated: 750/10,000 rows (7.5%) have data
```

### Configuration

You can adjust how many rows to check by modifying `streamlit_app.py`:

```python
# Check more rows (slower but more thorough)
validate_tag_column_in_file(upload_path, sheet_name='Data', sample_size=50000)

# Check ALL rows (slowest but 100% thorough)
validate_tag_column_in_file(upload_path, sheet_name='Data', sample_size=None)

# Check fewer rows (faster but less thorough)
validate_tag_column_in_file(upload_path, sheet_name='Data', sample_size=1000)
```

**Default**: 10,000 rows - good balance between speed and thoroughness

---

## Error: "Duplicate column names found"

### What This Error Means

This error occurs when trying to concatenate DataFrames that have overlapping column names. In our case, it happened because:
- The Excel file has a **Cost** column (actual cost data)
- The tag parser also extracts **Cost** from the Tags column
- When concatenating, we end up with two "Cost" columns

### What Was Fixed

**In `tag_parser.py`:**

```python
# BEFORE - caused duplicate Cost columns
parsed_df = pd.DataFrame(parsed_data.tolist())
parsed_df['Date'] = date_value
result_df = pd.concat([df, parsed_df], axis=1)  # Duplicates!

# AFTER - removes duplicates before concatenating
parsed_df = pd.DataFrame(parsed_data.tolist())
parsed_df['Date'] = date_value

# Remove Cost column from parsed_df if it exists in original df
if 'Cost' in df.columns and 'Cost' in parsed_df.columns:
    logger.info("Cost column exists in both - using original data")
    parsed_df = parsed_df.drop(columns=['Cost'])

# Check for any other duplicate columns
duplicate_cols = [col for col in parsed_df.columns if col in df.columns]
if duplicate_cols:
    logger.warning(f"Dropping duplicate columns: {duplicate_cols}")
    parsed_df = parsed_df.drop(columns=duplicate_cols)

result_df = pd.concat([df, parsed_df], axis=1)  # No duplicates!
```

**Key Points:**
- We **prioritize the actual Cost column** from Excel over cost from tags
- We **check for any duplicate columns** and remove them from parsed results
- The final DataFrame has only one Cost column (from Excel, not tags)

### Why This Approach?

The Cost column from your Excel file contains the **actual cost values**, which is what we want to store in MongoDB. The cost value in the Tags column (if present) is just metadata and should be ignored when there's a real Cost column.

---

## Error: "The truth value of a Series is ambiguous"

### What This Error Means

This error occurs when Python tries to evaluate a pandas Series in a boolean context (like an `if` statement) without being explicit about what to check.

**Example of what causes this:**
```python
# WRONG - causes the error
if some_series:
    ...

# CORRECT
if not some_series.empty:
    ...

# CORRECT
if some_series.any():
    ...
```

### What Was Fixed

We made several changes to prevent this error:

#### 1. **Tag Parser** (`src/processor/tag_parser.py`)

**Before:**
```python
if tag_column not in df.columns:  # Could be ambiguous
    ...

cost_count = parsed_df['Cost'].notna().sum()  # Returns numpy.int64
```

**After:**
```python
if tag_column not in list(df.columns):  # Explicit list check
    ...

cost_count = int(parsed_df['Cost'].notna().sum())  # Explicit int conversion
```

#### 2. **Streamlit UI** (`src/ui/streamlit_app.py`)

**Before:**
```python
cost_count = final_df['Cost'].notna().sum() if 'Cost' in final_df.columns else 0
if date_value:  # Could be ambiguous if date_value is a Series
    ...
```

**After:**
```python
# Wrapped in try-except with explicit checks
try:
    if 'Cost' in final_df.columns:
        cost_count = int(final_df['Cost'].notna().sum())
    else:
        cost_count = 0
except Exception as e:
    logger.warning(f"Error counting Cost column: {e}")
    cost_count = 0

# More explicit boolean check
if date_value is not None and str(date_value).strip():
    ...
```

#### 3. **Column Filtering**

**Before:**
```python
available_preview_cols = [col for col in preview_columns if col in final_df.columns]
```

**After:**
```python
available_preview_cols = [col for col in preview_columns if col in list(final_df.columns)]
```

### How to Prevent This Error in the Future

When working with pandas:

1. **Always convert Series to explicit types**:
   ```python
   count = int(df['column'].sum())  # Not just df['column'].sum()
   ```

2. **Use explicit boolean checks**:
   ```python
   if not df.empty:  # Not just if df:
   if series.any():  # Not just if series:
   ```

3. **Convert pandas Index to list when checking membership**:
   ```python
   if col_name in list(df.columns):  # Not just if col_name in df.columns:
   ```

4. **Wrap potentially problematic code in try-except**:
   ```python
   try:
       result = df[col].sum()
   except Exception as e:
       logger.error(f"Error: {e}")
       result = 0
   ```

### Testing the Fix

To verify the fix works:

1. **Start the Streamlit app**:
   ```bash
   cd /Users/davisgeorge/Documents/Claude/infra
   streamlit run src/ui/streamlit_app.py
   ```

2. **Upload your Excel file** with Summary and Data sheets

3. **Click "Process File"**

4. **Verify**:
   - No "truth value of a Series is ambiguous" error
   - Statistics are displayed correctly
   - Preview shows data correctly
   - Cost and Date counts are shown

### Other Common Pandas Errors

#### "Cannot compare types..."
**Cause**: Trying to compare mixed data types
**Fix**: Convert to same type first or use `.astype()`

#### "Cannot reindex from a duplicate axis"
**Cause**: Duplicate column or index names
**Fix**: Remove duplicates or use `.reset_index(drop=True)`

#### "KeyError: column name"
**Cause**: Column doesn't exist
**Fix**: Check with `if col in df.columns` first

#### "ValueError: cannot convert float NaN to integer"
**Cause**: Trying to convert NaN to int
**Fix**: Fill NaN first with `fillna(0)` or handle explicitly

### Debug Mode

If you encounter other errors, you can enable debug logging:

1. **Edit `config.py`**:
   ```python
   LOG_LEVEL = "DEBUG"  # Instead of "INFO"
   ```

2. **Check logs** to see detailed error information

3. **Look for warning messages** that indicate the source of the problem

### Getting Help

If you continue to see errors:

1. **Check the log file** in the `logs/` directory
2. **Look at the full error traceback** - it shows exactly where the error occurred
3. **Verify your Excel file structure**:
   - Summary sheet with "Start date:" label
   - Data sheet with Tags column
4. **Check data types** in your Excel columns (dates should be dates, numbers should be numbers)

### Quick Fixes

#### If date extraction fails:
- Check that Summary sheet exists
- Check that "Start date:" label exists
- Check that date is in a recognizable format

#### If tags parsing fails:
- Check that Data sheet exists
- Check that Tags column exists
- Check tag format matches one of the supported formats

#### If MongoDB insertion fails:
- Check MongoDB is running: `brew services list`
- Start MongoDB: `brew services start mongodb-community`
- Test connection in the UI

---

## Updated Code Summary

All boolean checks and Series operations are now explicit and safe:

✅ **Column membership checks** use `list(df.columns)`
✅ **Count operations** are wrapped in `int()`
✅ **Boolean conditionals** check for None explicitly
✅ **Exception handling** added for all Series operations
✅ **Preview operations** check for empty DataFrames

The code is now more robust and should handle edge cases without ambiguous Series errors!
