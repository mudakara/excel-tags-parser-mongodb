# MongoDB Dynamic Fields Update

## 🎯 Overview

MongoDB insertion has been updated to store **ALL dynamically extracted tag fields** at the top level of documents, not just the 5 predefined fields (applicationName, environment, owner, cost, date).

## ✅ What Changed

### Before ❌
Only 5 fields were stored at the top level:
```javascript
{
  "applicationName": "myapp",
  "environment": "production",
  "owner": "john",
  "cost": 1234.56,
  "date": "2025-11",
  // Other fields like primaryContact, usage, etc. were NOT at top level
  "tags": {...},
  "originalData": {...}
}
```

### After ✅
ALL dynamically extracted fields are stored at the top level:
```javascript
{
  // Standard fields
  "applicationName": "myapp",
  "environment": "production",
  "owner": "john",
  "cost": 1234.56,
  "date": "2025-11",

  // ALL dynamic fields from tags (in camelCase)
  "primaryContact": "jane doe",
  "usage": "databricks prod env",
  "department": "IT",
  "costCenter": "CC123",
  "team": "analytics",
  "project": "sales",
  // ... any other fields extracted from tags

  "tags": {
    "raw": "...",
    "parsed": {
      // All fields also stored here
    }
  },
  "originalData": {...},
  "metadata": {...}
}
```

## 🔧 Technical Changes

### 1. New Helper Function: `to_camel_case()`
**File:** `src/database/mongodb_operations.py`

Converts column names to camelCase for MongoDB field names:
- `'Primary Contact'` → `'primaryContact'`
- `'Cost Center'` → `'costCenter'`
- `'Application Name'` → `'applicationName'`

### 2. Updated `prepare_document()` Function
**File:** `src/database/mongodb_operations.py`

Now extracts ALL non-system columns as dynamic fields:
- Identifies system columns (Tags, Date, Cost columns)
- Extracts all other columns with non-null values
- Converts column names to camelCase
- Adds them to top level of MongoDB document
- Also stores them in `tags.parsed`

### 3. Updated Progress Callback Integration
**File:** `src/ui/streamlit_app.py`

MongoDB insertion now shows real-time progress:
- Document preparation progress
- Batch insertion progress
- Index creation status

## 📊 MongoDB Document Structure

### Complete Structure
```javascript
{
  // === Standard Fields (always at top level) ===
  "applicationName": "myapp",
  "environment": "production",
  "owner": "john",
  "cost": 1234.56,
  "date": "2025-11",

  // === Dynamic Fields (automatically extracted from tags) ===
  "primaryContact": "jane doe",
  "usage": "databricks prod env",
  "department": "IT",
  "costCenter": "CC123",
  "businessUnit": "Corporate",
  "team": "Analytics",
  "project": "Sales Dashboard",
  // ... unlimited fields based on your tags

  // === Tags Section ===
  "tags": {
    "raw": "\"primarycontact\":\"jane doe\",\"usage\":\"databricks prod env\"",
    "parsed": {
      // All extracted fields also stored here
      "applicationName": "myapp",
      "environment": "production",
      "owner": "john",
      "primaryContact": "jane doe",
      "usage": "databricks prod env",
      "department": "IT",
      "costCenter": "CC123"
    }
  },

  // === Original Data (everything from Excel) ===
  "originalData": {
    // Complete row data from Excel file
  },

  // === Metadata ===
  "metadata": {
    "importDate": "2025-11-15T17:21:31.894719",
    "sourceFile": "november.xlsx",
    "importTimestamp": "2025-11-15T17:21:31.894719",
    "dataDate": "2025-11"
  }
}
```

## 🎨 Field Naming Convention

All field names are converted to camelCase for MongoDB:

| Excel Column | MongoDB Field |
|--------------|---------------|
| Primary Contact | primaryContact |
| Cost Center | costCenter |
| Application Name | applicationName |
| Business Unit | businessUnit |
| Department | department |
| Usage | usage |
| Team | team |
| Project | project |

## 🔍 Querying Dynamic Fields

Now you can easily query by ANY dynamically extracted field:

```javascript
// Find all documents with a specific primary contact
db.collection.find({ "primaryContact": "jane doe" })

// Find by usage
db.collection.find({ "usage": /databricks/ })

// Find by department
db.collection.find({ "department": "IT" })

// Aggregate by cost center
db.collection.aggregate([
  { $group: { _id: "$costCenter", total: { $sum: "$cost" } } }
])

// Filter by multiple dynamic fields
db.collection.find({
  "department": "IT",
  "costCenter": "CC123",
  "environment": "production"
})
```

## ✨ Benefits

1. **Flexible Querying**: Query by ANY field extracted from tags
2. **Better Analytics**: Aggregate and group by any dimension
3. **Future-Proof**: New tag fields automatically become queryable
4. **Clean Structure**: All fields at top level (no need to drill into nested objects)
5. **Preserved Data**: Original data still in `originalData` for reference

## 🧪 Testing

Run the test script to verify dynamic field extraction:

```bash
./test_dynamic_mongodb.py
# or
mcp_server/venv/bin/python3 test_dynamic_mongodb.py
```

The test verifies:
- camelCase conversion
- Dynamic field extraction
- Top-level field placement
- tags.parsed structure

## 📝 Example Use Cases

### Use Case 1: Cost Center Analysis
```javascript
// Total cost by cost center
db.collection.aggregate([
  { $match: { "costCenter": { $exists: true, $ne: null } } },
  { $group: {
      _id: "$costCenter",
      totalCost: { $sum: "$cost" },
      count: { $sum: 1 }
  } },
  { $sort: { totalCost: -1 } }
])
```

### Use Case 2: Primary Contact Filtering
```javascript
// Find all resources for a specific contact
db.collection.find({
  "primaryContact": "jane doe",
  "date": "2025-11"
})
```

### Use Case 3: Usage Pattern Analysis
```javascript
// Find all databricks usage
db.collection.find({
  "usage": /databricks/i
})
```

## 🚀 Migration

If you have existing data in MongoDB:

1. **Option 1: Clear and Re-import**
   ```python
   from src.database.mongodb_operations import clear_collection
   clear_collection()  # Warning: Deletes all data!
   # Then re-import your Excel files
   ```

2. **Option 2: Keep Old Data**
   - Old documents will have the old structure
   - New documents will have the new structure with dynamic fields
   - Both can coexist in the same collection

## 📚 Related Files

- `src/database/mongodb_operations.py` - MongoDB operations with dynamic field extraction
- `src/processor/tag_parser.py` - Tag parsing with dynamic field extraction
- `src/ui/streamlit_app.py` - UI with progress callbacks
- `DYNAMIC_PARSING_GUIDE.md` - Guide for dynamic tag parsing
- `test_dynamic_mongodb.py` - Test script for verification

## 🎉 Summary

**Before**: Only 5 predefined fields stored in MongoDB
**After**: ALL dynamically extracted fields stored at top level for easy querying

This makes your MongoDB data much more flexible and queryable without any schema changes!
