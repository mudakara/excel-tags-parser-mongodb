"""
Validation utilities for file and data validation
"""
import os
import pandas as pd
import logging
from typing import Tuple, List
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config

logger = logging.getLogger(__name__)


def validate_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate that a file exists and is a valid Excel file.

    Args:
        file_path: Path to the file to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return False, f"File does not exist: {file_path}"

    # Check if it's a file (not a directory)
    if not os.path.isfile(file_path):
        return False, f"Path is not a file: {file_path}"

    # Check file extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in config.ALLOWED_EXTENSIONS:
        return False, f"Invalid file extension: {ext}. Allowed: {config.ALLOWED_EXTENSIONS}"

    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > config.MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed ({config.MAX_FILE_SIZE_MB} MB)"

    return True, ""


def validate_columns(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, str]:
    """
    Validate that a DataFrame contains required columns.

    Args:
        df: DataFrame to validate
        required_columns: List of column names that must be present

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string
    """
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        return False, f"Missing required columns: {missing_columns}. Available columns: {df.columns.tolist()}"

    return True, ""


def validate_tag_column(df: pd.DataFrame, tag_column: str = None) -> Tuple[bool, str]:
    """
    Validate that the Tags column exists and is not empty.

    NOTE: This function only checks if the column exists.
    It does NOT fail if column is empty, as data might be in later rows.
    Use validate_tag_column_in_file() for full file validation.

    Args:
        df: DataFrame to validate (can be just a preview/sample)
        tag_column: Name of the tags column (default from config)

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string
    """
    if tag_column is None:
        tag_column = config.TAG_COLUMN

    # Check if column exists
    is_valid, error_msg = validate_columns(df, [tag_column])
    if not is_valid:
        return False, error_msg

    # Just warn if first few rows are empty, don't fail
    # (later rows might have data)
    empty_count = df[tag_column].isna().sum()
    total_count = len(df)

    if empty_count == total_count:
        logger.warning(f"Column '{tag_column}' is empty in first {total_count} rows - will check full file during processing")
    elif empty_count > 0:
        empty_percentage = (empty_count / total_count) * 100
        logger.info(f"Column '{tag_column}' has {empty_count}/{total_count} ({empty_percentage:.1f}%) empty values in preview")

    return True, ""


def validate_tag_column_in_file(file_path: str, sheet_name: str = 'Data', tag_column: str = None, sample_size: int = None) -> Tuple[bool, str, dict]:
    """
    Validate that the Tags column exists and has data by reading the actual file.

    This function reads the entire file (or a large sample) to check if the Tags
    column has ANY non-empty values before declaring it completely empty.

    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to read (default: 'Data')
        tag_column: Name of the tags column (default from config)
        sample_size: Number of rows to read (None = read all rows)

    Returns:
        Tuple of (is_valid, error_message, statistics_dict)
        statistics_dict contains: total_rows, empty_rows, non_empty_rows, empty_percentage
    """
    if tag_column is None:
        tag_column = config.TAG_COLUMN

    try:
        # Read the file (all rows or sample)
        if sample_size is not None:
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=sample_size, engine='openpyxl')
            logger.info(f"Reading sample of {sample_size} rows for validation")
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            logger.info(f"Reading entire file for validation")

    except Exception as e:
        return False, f"Error reading file: {str(e)}", {}

    # Check if column exists
    if tag_column not in df.columns:
        return False, f"Column '{tag_column}' not found. Available: {df.columns.tolist()}", {}

    # Calculate statistics
    total_rows = len(df)
    empty_rows = int(df[tag_column].isna().sum())
    non_empty_rows = total_rows - empty_rows
    empty_percentage = (empty_rows / total_rows * 100) if total_rows > 0 else 0

    stats = {
        'total_rows': total_rows,
        'empty_rows': empty_rows,
        'non_empty_rows': non_empty_rows,
        'empty_percentage': empty_percentage
    }

    # Check if column is completely empty
    if non_empty_rows == 0:
        return False, f"Column '{tag_column}' is completely empty (checked {total_rows} rows)", stats

    # Warn if mostly empty
    if empty_percentage > 75:
        logger.warning(f"Column '{tag_column}' is {empty_percentage:.1f}% empty ({empty_rows}/{total_rows} rows)")

    logger.info(f"Column '{tag_column}' validation: {non_empty_rows}/{total_rows} rows have data ({100-empty_percentage:.1f}%)")

    return True, "", stats


def validate_excel_file(file_path: str) -> Tuple[bool, str]:
    """
    Comprehensive validation of an Excel file.

    Checks:
    1. File exists and is valid Excel
    2. File can be read
    3. File contains data

    Args:
        file_path: Path to the Excel file

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate file
    is_valid, error_msg = validate_file(file_path)
    if not is_valid:
        return False, error_msg

    # Try to read the file
    try:
        df = pd.read_excel(file_path, nrows=5, engine='openpyxl')
    except Exception as e:
        return False, f"Cannot read Excel file: {str(e)}"

    # Check if file has data
    if len(df) == 0:
        return False, "Excel file is empty"

    return True, ""


def validate_uploaded_file(uploaded_file) -> Tuple[bool, str]:
    """
    Validate a Streamlit uploaded file object.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Tuple of (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "No file uploaded"

    # Check file extension
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in config.ALLOWED_EXTENSIONS:
        return False, f"Invalid file extension: {file_ext}. Allowed: {config.ALLOWED_EXTENSIONS}"

    # Check file size
    if hasattr(uploaded_file, 'size'):
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > config.MAX_FILE_SIZE_MB:
            return False, f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed ({config.MAX_FILE_SIZE_MB} MB)"

    return True, ""
