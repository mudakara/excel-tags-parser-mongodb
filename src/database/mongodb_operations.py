"""
MongoDB operations module for data insertion and querying
"""
import pandas as pd
from pymongo.collection import Collection
from datetime import datetime
from typing import Dict, List, Any
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config
from src.database.mongodb_client import get_collection

logger = logging.getLogger(__name__)


def prepare_document(row: pd.Series, source_file: str = None) -> Dict[str, Any]:
    """
    Prepare a single document for MongoDB insertion.

    Schema design optimized for dashboards and analytics:
    - All original Excel columns preserved
    - Extracted fields: applicationName, environment, owner
    - Metadata: importDate, sourceFile
    - Clean data: NaN converted to None

    Args:
        row: DataFrame row as Series
        source_file: Name of the source Excel file

    Returns:
        Dictionary ready for MongoDB insertion
    """
    # Convert row to dictionary and replace NaN with None
    doc = row.to_dict()

    # Get cost from the Cost column BEFORE replacing NaN (to preserve raw value)
    # Try different possible column names for cost
    cost_value = None
    cost_column_found = None

    for cost_key in ['Cost', 'CostUSD', 'cost', 'COST', 'PreTaxCost', 'CostInBillingCurrency']:
        if cost_key in doc:
            raw_cost = doc.get(cost_key)
            # Check if value exists and is not NaN
            if raw_cost is not None and not pd.isna(raw_cost):
                cost_value = raw_cost
                cost_column_found = cost_key
                logger.info(f"Found cost value from column '{cost_key}': {cost_value}")
                break
            elif cost_key in doc:
                logger.debug(f"Column '{cost_key}' exists but value is NaN or None")

    # If cost is still None, log available columns for debugging
    if cost_value is None:
        logger.warning(f"Cost value is None. Available columns: {list(doc.keys())[:20]}")  # Show first 20 columns

    # Replace pandas NaN/NaT with None for proper JSON serialization
    for key, value in doc.items():
        if pd.isna(value):
            doc[key] = None
        elif isinstance(value, (pd.Timestamp, datetime)):
            doc[key] = value.isoformat()

    # Restructure for better querying and dashboard creation
    structured_doc = {
        # Extracted fields (for easy filtering/grouping in dashboards)
        'applicationName': doc.get('Application Name'),
        'environment': doc.get('Environment'),
        'owner': doc.get('Owner'),
        'cost': cost_value,  # Taken directly from Cost column
        'date': doc.get('Date'),  # Date extracted from Summary sheet (YYYY-MM format)

        # Tags information
        'tags': {
            'raw': doc.get('Tags'),
            'parsed': {
                'applicationName': doc.get('Application Name'),
                'environment': doc.get('Environment'),
                'owner': doc.get('Owner')
            }
        },

        # All original data from Excel (preserves all columns)
        'originalData': doc,

        # Metadata for tracking
        'metadata': {
            'importDate': datetime.utcnow(),
            'sourceFile': source_file,
            'importTimestamp': datetime.utcnow().isoformat(),
            'dataDate': doc.get('Date')  # Also store in metadata for easy access
        }
    }

    return structured_doc


def insert_dataframe_to_mongodb(
    df: pd.DataFrame,
    source_file: str = None,
    collection_name: str = None,
    batch_size: int = 1000
) -> Dict[str, Any]:
    """
    Insert DataFrame into MongoDB with proper schema design.

    The schema is optimized for:
    - Fast querying by applicationName, environment, owner
    - Dashboard creation with aggregations
    - Historical tracking with importDate
    - Preserving all original Excel data

    Args:
        df: DataFrame to insert
        source_file: Name of the source Excel file
        collection_name: MongoDB collection name (default from config)
        batch_size: Number of documents to insert per batch

    Returns:
        Dictionary with insertion statistics
    """
    collection = get_collection(collection_name)

    logger.info(f"Preparing to insert {len(df)} documents into MongoDB")

    # Prepare all documents
    documents = []
    for idx, row in df.iterrows():
        doc = prepare_document(row, source_file)
        documents.append(doc)

    # Insert in batches for better performance
    total_inserted = 0
    failed_inserts = 0

    try:
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]

            try:
                result = collection.insert_many(batch, ordered=False)
                total_inserted += len(result.inserted_ids)
                logger.info(f"Inserted batch: {len(result.inserted_ids)} documents")

            except Exception as e:
                failed_inserts += len(batch)
                logger.error(f"Error inserting batch: {e}")

        logger.info(f"Successfully inserted {total_inserted} documents")

        # Create indexes after insertion
        create_indexes(collection)

        return {
            'success': True,
            'total_documents': len(df),
            'inserted': total_inserted,
            'failed': failed_inserts,
            'collection': collection.name,
            'database': collection.database.name
        }

    except Exception as e:
        logger.error(f"Error during MongoDB insertion: {e}")
        return {
            'success': False,
            'error': str(e),
            'total_documents': len(df),
            'inserted': total_inserted,
            'failed': failed_inserts
        }


def create_indexes(collection: Collection = None) -> None:
    """
    Create indexes on MongoDB collection for better query performance.

    Indexes are created on:
    - applicationName (for filtering by app)
    - environment (for filtering by env)
    - owner (for filtering by owner)
    - metadata.importDate (for time-based queries)
    - Compound index on applicationName + environment

    Args:
        collection: MongoDB collection (default from config)
    """
    if collection is None:
        collection = get_collection()

    logger.info("Creating indexes for better query performance")

    try:
        # Single field indexes
        collection.create_index('applicationName')
        collection.create_index('environment')
        collection.create_index('owner')
        collection.create_index('cost')
        collection.create_index('date')  # Index for date field (YYYY-MM format)
        collection.create_index('metadata.importDate')

        # Compound indexes for common query patterns
        collection.create_index([('applicationName', 1), ('environment', 1)])
        collection.create_index([('environment', 1), ('owner', 1)])
        collection.create_index([('environment', 1), ('cost', 1)])
        collection.create_index([('date', 1), ('environment', 1)])  # Date + environment queries
        collection.create_index([('date', 1), ('applicationName', 1)])  # Date + app queries

        # Text index for searching
        collection.create_index([('tags.raw', 'text')])

        logger.info("Successfully created all indexes")

    except Exception as e:
        logger.warning(f"Error creating indexes (may already exist): {e}")


def get_statistics(collection_name: str = None) -> Dict[str, Any]:
    """
    Get statistics about the MongoDB collection for dashboards.

    Args:
        collection_name: MongoDB collection name (default from config)

    Returns:
        Dictionary with collection statistics
    """
    collection = get_collection(collection_name)

    try:
        stats = {
            'total_documents': collection.count_documents({}),
            'unique_applications': len(collection.distinct('applicationName')),
            'unique_environments': len(collection.distinct('environment')),
            'unique_owners': len(collection.distinct('owner')),
            'applications': collection.distinct('applicationName'),
            'environments': collection.distinct('environment'),
            'owners': collection.distinct('owner')
        }

        logger.info(f"Collection statistics: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {}


def query_by_filters(
    application_name: str = None,
    environment: str = None,
    owner: str = None,
    collection_name: str = None
) -> List[Dict]:
    """
    Query documents with filters (useful for dashboards).

    Args:
        application_name: Filter by application name
        environment: Filter by environment
        owner: Filter by owner
        collection_name: MongoDB collection name (default from config)

    Returns:
        List of matching documents
    """
    collection = get_collection(collection_name)

    query = {}
    if application_name:
        query['applicationName'] = application_name
    if environment:
        query['environment'] = environment
    if owner:
        query['owner'] = owner

    try:
        results = list(collection.find(query))
        logger.info(f"Query returned {len(results)} documents")
        return results

    except Exception as e:
        logger.error(f"Error querying collection: {e}")
        return []


def clear_collection(collection_name: str = None) -> bool:
    """
    Clear all documents from a collection (use with caution).

    Args:
        collection_name: MongoDB collection name (default from config)

    Returns:
        True if successful, False otherwise
    """
    collection = get_collection(collection_name)

    try:
        result = collection.delete_many({})
        logger.warning(f"Deleted {result.deleted_count} documents from {collection.name}")
        return True

    except Exception as e:
        logger.error(f"Error clearing collection: {e}")
        return False
