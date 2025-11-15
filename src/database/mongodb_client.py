"""
MongoDB client connection module
"""
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config

logger = logging.getLogger(__name__)

# Global MongoDB client instance
_mongodb_client = None


def get_mongodb_client() -> MongoClient:
    """
    Get MongoDB client instance (singleton pattern).

    Returns:
        MongoClient instance

    Raises:
        ConnectionError: If unable to connect to MongoDB
    """
    global _mongodb_client

    if _mongodb_client is None:
        try:
            logger.info(f"Connecting to MongoDB at {config.MONGODB_URI}")
            _mongodb_client = MongoClient(
                config.MONGODB_URI,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )

            # Test connection
            _mongodb_client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionError(f"Could not connect to MongoDB at {config.MONGODB_URI}. Error: {e}")

    return _mongodb_client


def get_database(db_name: str = None) -> Database:
    """
    Get MongoDB database instance.

    Args:
        db_name: Database name (default from config)

    Returns:
        Database instance
    """
    if db_name is None:
        db_name = config.MONGODB_DATABASE

    client = get_mongodb_client()
    logger.info(f"Accessing database: {db_name}")
    return client[db_name]


def get_collection(collection_name: str = None, db_name: str = None) -> Collection:
    """
    Get MongoDB collection instance.

    Args:
        collection_name: Collection name (default from config)
        db_name: Database name (default from config)

    Returns:
        Collection instance
    """
    if collection_name is None:
        collection_name = config.MONGODB_COLLECTION

    db = get_database(db_name)
    logger.info(f"Accessing collection: {collection_name}")
    return db[collection_name]


def test_connection() -> bool:
    """
    Test MongoDB connection.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = get_mongodb_client()
        client.admin.command('ping')
        logger.info("MongoDB connection test successful")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection test failed: {e}")
        return False


def close_connection():
    """
    Close MongoDB connection.
    """
    global _mongodb_client

    if _mongodb_client is not None:
        _mongodb_client.close()
        _mongodb_client = None
        logger.info("MongoDB connection closed")
