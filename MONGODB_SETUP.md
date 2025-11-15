# MongoDB Integration Guide

## Overview

The Excel Tags Parser now includes MongoDB integration to store processed data for creating charts and dashboards. The data is stored with a well-designed schema optimized for analytics and querying.

## Database Schema Design

### Document Structure

Each row from the Excel file is stored as a document with the following structure:

```json
{
  "applicationName": "arcesb",
  "environment": "production",
  "owner": "data",

  "tags": {
    "raw": "\"owner\":\"data\",\"environment\":\"production\",\"applicationname\":\"arcesb\"",
    "parsed": {
      "applicationName": "arcesb",
      "environment": "production",
      "owner": "data"
    }
  },

  "originalData": {
    // All original Excel columns preserved here
    "Tags": "...",
    "Application Name": "arcesb",
    "Environment": "production",
    "Owner": "data",
    // ... other columns
  },

  "metadata": {
    "importDate": ISODate("2025-01-13T10:30:00Z"),
    "sourceFile": "azure.xlsx",
    "importTimestamp": "2025-01-13T10:30:00.123Z"
  }
}
```

### Design Benefits

1. **Top-level fields** (`applicationName`, `environment`, `owner`) for fast filtering and grouping
2. **originalData** preserves all Excel columns for detailed analysis
3. **metadata** tracks when and from where data was imported
4. **Indexes** on key fields for fast queries

## Installation

### 1. Install MongoDB

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
```

**Ubuntu/Debian:**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

**Windows:**
Download installer from: https://www.mongodb.com/try/download/community

### 2. Start MongoDB

**macOS:**
```bash
brew services start mongodb-community@7.0
```

**Linux:**
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Windows:**
MongoDB runs as a service automatically after installation.

### 3. Verify MongoDB is Running

```bash
mongosh
```

You should see the MongoDB shell. Type `exit` to quit.

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### 1. Process Excel File

Run the Streamlit application:
```bash
streamlit run src/ui/streamlit_app.py
```

### 2. Upload and Process

1. Upload your Excel file
2. Click "Process File"
3. Wait for processing to complete

### 3. Push to MongoDB

After processing, click the **"Push to MongoDB"** button to:
- Test MongoDB connection
- Insert all processed rows into the database
- Create indexes for performance
- Show insertion statistics

### 4. View Statistics

After pushing to MongoDB, expand "View Database Statistics" to see:
- Total documents in database
- Unique applications, environments, owners
- Lists of all values

## Querying Data

### Using MongoDB Shell

```bash
mongosh
use azure
```

**Get all documents:**
```javascript
db.resources.find().pretty()
```

**Filter by application:**
```javascript
db.resources.find({ applicationName: "arcesb" })
```

**Filter by environment:**
```javascript
db.resources.find({ environment: "production" })
```

**Count documents by environment:**
```javascript
db.resources.aggregate([
  { $group: { _id: "$environment", count: { $sum: 1 } } }
])
```

**Get unique applications:**
```javascript
db.resources.distinct("applicationName")
```

**Find resources by owner:**
```javascript
db.resources.find({ owner: "data" })
```

**Complex query (app + environment):**
```javascript
db.resources.find({
  applicationName: "arcesb",
  environment: "production"
})
```

### Using Python

```python
from src.database.mongodb_operations import query_by_filters, get_statistics

# Get all resources for a specific application
results = query_by_filters(application_name="arcesb")

# Get all production resources
results = query_by_filters(environment="production")

# Get resources by owner
results = query_by_filters(owner="data")

# Get statistics
stats = get_statistics()
print(f"Total documents: {stats['total_documents']}")
print(f"Applications: {stats['applications']}")
```

## Creating Dashboards

### Recommended Tools

1. **MongoDB Charts** (Native MongoDB visualization)
   - Free with MongoDB Atlas
   - Connect to local MongoDB
   - Create charts and dashboards

2. **Metabase** (Open-source BI tool)
   ```bash
   docker run -d -p 3000:3000 --name metabase metabase/metabase
   ```

3. **Apache Superset**
   ```bash
   pip install apache-superset
   ```

4. **Grafana** (with MongoDB plugin)

### Sample Queries for Dashboards

**Resources by Environment:**
```javascript
db.resources.aggregate([
  { $group: { _id: "$environment", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

**Resources by Application:**
```javascript
db.resources.aggregate([
  { $group: { _id: "$applicationName", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])
```

**Resources by Owner:**
```javascript
db.resources.aggregate([
  { $group: { _id: "$owner", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

**Imports Over Time:**
```javascript
db.resources.aggregate([
  { $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$metadata.importDate" } },
      count: { $sum: 1 }
  }},
  { $sort: { _id: 1 } }
])
```

**Matrix: Application x Environment:**
```javascript
db.resources.aggregate([
  { $group: {
      _id: { app: "$applicationName", env: "$environment" },
      count: { $sum: 1 }
  }},
  { $sort: { "_id.app": 1, "_id.env": 1 } }
])
```

## Indexes

The following indexes are automatically created for performance:

- `applicationName` (single field)
- `environment` (single field)
- `owner` (single field)
- `metadata.importDate` (single field)
- `applicationName + environment` (compound)
- `environment + owner` (compound)
- `tags.raw` (text search)

## Configuration

Edit `config.py` to customize MongoDB settings:

```python
# MongoDB configuration
MONGODB_URI = 'mongodb://localhost:27017/'
MONGODB_DATABASE = 'azure'
MONGODB_COLLECTION = 'resources'

# MongoDB indexes
MONGODB_INDEXES = [
    'Application Name',
    'Environment',
    'Owner'
]
```

## Backup and Restore

### Backup Database

```bash
mongodump --db azure --out /path/to/backup
```

### Restore Database

```bash
mongorestore --db azure /path/to/backup/azure
```

### Export to JSON

```bash
mongoexport --db azure --collection resources --out resources.json
```

### Import from JSON

```bash
mongoimport --db azure --collection resources --file resources.json
```

## Troubleshooting

### Cannot Connect to MongoDB

**Error:** `Cannot connect to MongoDB at mongodb://localhost:27017/`

**Solution:**
```bash
# Check if MongoDB is running
brew services list  # macOS
sudo systemctl status mongod  # Linux

# Start MongoDB
brew services start mongodb-community@7.0  # macOS
sudo systemctl start mongod  # Linux
```

### Connection Timeout

**Error:** `ServerSelectionTimeoutError`

**Solution:**
- Check firewall settings
- Verify MongoDB is listening on port 27017
- Try connecting with `mongosh`

### Authentication Required

If your MongoDB requires authentication, update `config.py`:

```python
MONGODB_URI = 'mongodb://username:password@localhost:27017/?authSource=admin'
```

## Performance Tips

1. **Batch Size:** Default is 1000 documents per batch. Adjust in code if needed.
2. **Indexes:** Created automatically. Don't delete them.
3. **Query Optimization:** Always use indexed fields in queries.
4. **Memory:** MongoDB uses available RAM for caching.

## Security Considerations

For production use:

1. Enable authentication
2. Create dedicated user with limited permissions
3. Use environment variables for credentials
4. Enable SSL/TLS
5. Configure firewall rules

## API Reference

### MongoDB Operations

```python
# Insert DataFrame
from src.database.mongodb_operations import insert_dataframe_to_mongodb

result = insert_dataframe_to_mongodb(
    df=processed_df,
    source_file="azure.xlsx",
    collection_name="resources",  # optional
    batch_size=1000  # optional
)

# Get statistics
from src.database.mongodb_operations import get_statistics

stats = get_statistics()

# Query with filters
from src.database.mongodb_operations import query_by_filters

results = query_by_filters(
    application_name="arcesb",
    environment="production",
    owner="data"
)

# Clear collection (use with caution!)
from src.database.mongodb_operations import clear_collection

clear_collection()
```

## Next Steps

1. Set up MongoDB Charts or Metabase
2. Create custom dashboards
3. Set up automated backups
4. Configure monitoring (MongoDB Atlas or Prometheus)
5. Add custom aggregation queries for your use case
