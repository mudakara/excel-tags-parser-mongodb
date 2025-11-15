"""
Configuration settings for Excel Tags Parser application
"""
import os

# Application settings
CHUNK_SIZE = 10000  # Rows per chunk for processing
MAX_FILE_SIZE_MB = 500  # Maximum upload file size in MB
ALLOWED_EXTENSIONS = ['.xlsx', '.xls']

# Performance settings
NUM_WORKERS = 4  # Number of parallel workers for multiprocessing
ENABLE_PARALLEL_PROCESSING = False  # Set to True for parallel processing

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'data', 'uploads')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Tag parsing configuration
TAG_SEPARATORS = [',', ';', '|']
KEY_VALUE_SEPARATOR = ':'

# Column names
TAG_COLUMN = 'Tags'
NEW_COLUMNS = {
    'application': 'Application Name',
    'environment': 'Environment',
    'owner': 'Owner'
}

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# File naming
OUTPUT_FILENAME_PREFIX = 'processed_'
OUTPUT_FILENAME_TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'

# MongoDB configuration
MONGODB_URI = 'mongodb://localhost:27017/'
MONGODB_DATABASE = 'azure'
MONGODB_COLLECTION = 'resources'

# MongoDB indexes for performance
MONGODB_INDEXES = [
    'Application Name',
    'Environment',
    'Owner'
]
