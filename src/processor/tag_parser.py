"""
Tag parsing module for dynamically extracting ALL key-value pairs from Tags column
"""
import pandas as pd
import re
import logging
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config

logger = logging.getLogger(__name__)

# Pre-compile regex patterns for better performance
KEY_VALUE_PATTERN = re.compile(r'([^:,;|]+):([^:,;|]+)')


def format_column_name(key: str) -> str:
    """
    Format a tag key into a proper column name.

    Examples:
        'primarycontact' -> 'Primary Contact'
        'application_name' -> 'Application Name'
        'costcenter' -> 'Cost Center'

    Args:
        key: The raw key from tags

    Returns:
        Formatted column name
    """
    # Replace underscores with spaces
    key = key.replace('_', ' ')

    # Handle common abbreviations and special cases
    special_cases = {
        'applicationname': 'Application Name',
        'application name': 'Application Name',
        'env': 'Environment',
        'environment': 'Environment',
        'owner': 'Owner',
        'cost': 'Cost',
        'primarycontact': 'Primary Contact',
        'primary contact': 'Primary Contact',
        'usage': 'Usage',
        'costcenter': 'Cost Center',
        'cost center': 'Cost Center',
        'businessunit': 'Business Unit',
        'business unit': 'Business Unit',
        'department': 'Department',
        'project': 'Project',
        'team': 'Team',
    }

    key_lower = key.lower().strip()

    # Check special cases first
    if key_lower in special_cases:
        return special_cases[key_lower]

    # Title case for everything else
    return key.strip().title()


def parse_tags(tag_string: Any) -> Dict[str, str]:
    """
    Parse tags column and dynamically extract ALL key-value pairs.

    This function extracts ALL fields found in the tags, not just predefined ones.
    Each key becomes a column name (properly formatted) and the value becomes the cell value.

    Supports multiple tag formats:
    1. Escaped JSON: "\"owner\":\"data\",\"environment\":\"production\",\"primarycontact\":\"john doe\""
    2. Key-value pairs: "applicationname:myapp,environment:prod,owner:john,usage:databricks"
    3. JSON format: '{"applicationname": "myapp", "environment": "prod", "owner": "john"}'
    4. Pipe-separated values: "myapp|prod|john" (limited support - uses predefined field order)

    Args:
        tag_string: The tag string to parse (from Tags column)

    Returns:
        Dictionary with ALL key-value pairs found
        Keys are formatted as proper column names (e.g., 'Primary Contact')
        Returns empty dict if parsing fails or no data found

    Examples:
        >>> parse_tags('"owner":"data","primarycontact":"john doe"')
        {'Owner': 'data', 'Primary Contact': 'john doe'}

        >>> parse_tags("applicationname:myapp,usage:databricks prod")
        {'Application Name': 'myapp', 'Usage': 'databricks prod'}
    """
    result = {}

    # Handle empty or NaN values
    if pd.isna(tag_string) or tag_string is None:
        return result

    tag_string = str(tag_string).strip()

    if not tag_string:
        return result

    try:
        # First, handle escaped JSON strings (unescape them)
        if '\\' in tag_string:
            # Remove surrounding quotes if present
            if tag_string.startswith('"') and tag_string.endswith('"'):
                tag_string = tag_string[1:-1]

            # Replace escaped quotes with regular quotes
            tag_string = tag_string.replace('\\"', '"')
            tag_string = tag_string.replace('\\\\', '\\')

        # Strategy 1: Try JSON format first (most structured)
        if (tag_string.startswith('{') and tag_string.endswith('}')) or ('"' in tag_string and ':' in tag_string):
            # Try to parse as JSON
            result = _parse_json_format(tag_string)
            # If JSON parsing didn't extract anything, try escaped key-value format
            if not result:
                result = _parse_escaped_key_value_format(tag_string)

        # Strategy 2: Key-value pairs (most common format)
        elif ':' in tag_string:
            result = _parse_key_value_format(tag_string)

        # Strategy 3: Pipe-separated ordered values (limited - uses predefined fields)
        elif '|' in tag_string:
            result = _parse_pipe_separated_format(tag_string)

        # Strategy 4: No recognizable format
        else:
            logger.debug(f"No matching format for tag: {tag_string}")

    except Exception as e:
        logger.warning(f"Error parsing tag '{tag_string}': {e}")

    return result


def _parse_escaped_key_value_format(tag_string: str) -> Dict[str, str]:
    """
    Parse escaped JSON key-value format tags and extract ALL key-value pairs.

    Format: "owner":"data","environment":"production","primarycontact":"john doe","usage":"databricks"

    Returns:
        Dictionary with ALL key-value pairs found, with formatted column names
    """
    result = {}

    # Use regex to extract quoted key-value pairs
    # Pattern: "key":"value"
    pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
    matches = re.findall(pattern, tag_string)

    for key, value in matches:
        key_raw = key.strip()
        value_clean = value.strip()

        # Format the key into a proper column name
        column_name = format_column_name(key_raw)

        # Store the value
        result[column_name] = value_clean

    return result


def _parse_key_value_format(tag_string: str) -> Dict[str, str]:
    """
    Parse key-value format tags and extract ALL key-value pairs.

    Formats: "applicationname:myapp,environment:prod,owner:john,usage:databricks,primarycontact:john doe"

    Returns:
        Dictionary with ALL key-value pairs found, with formatted column names
    """
    result = {}

    # Split by common separators
    pairs = re.split(r'[,;]', tag_string)

    for pair in pairs:
        pair = pair.strip()
        if ':' not in pair:
            continue

        try:
            key, value = pair.split(':', 1)
            key_raw = key.strip()
            value = value.strip()

            # Remove surrounding quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            # Format the key into a proper column name
            column_name = format_column_name(key_raw)

            # Store the value
            result[column_name] = value

        except ValueError:
            continue

    return result


def _parse_pipe_separated_format(tag_string: str) -> Dict[str, str]:
    """
    Parse pipe-separated format with ordered values.

    Format: "myapp|production|john|1000" (application|environment|owner|cost)
    """
    result = {
        'Application Name': None,
        'Environment': None,
        'Owner': None,
        'Cost': None
    }

    parts = [p.strip() for p in tag_string.split('|')]

    # Assume order: Application | Environment | Owner | Cost
    if len(parts) >= 1 and parts[0]:
        result['Application Name'] = parts[0]
    if len(parts) >= 2 and parts[1]:
        result['Environment'] = parts[1]
    if len(parts) >= 3 and parts[2]:
        result['Owner'] = parts[2]
    if len(parts) >= 4 and parts[3]:
        result['Cost'] = parts[3]

    return result


def _parse_json_format(tag_string: str) -> Dict[str, str]:
    """
    Parse JSON-like format tags and extract ALL key-value pairs.

    Format: '{"applicationname": "myapp", "environment": "prod", "owner": "john", "usage": "databricks"}'

    Returns:
        Dictionary with ALL key-value pairs found, with formatted column names
    """
    import json

    result = {}

    try:
        # Try to parse as proper JSON first
        if tag_string.startswith('{') and tag_string.endswith('}'):
            data = json.loads(tag_string)

            # Extract ALL key-value pairs
            for key, value in data.items():
                key_raw = key.strip()

                # Format the key into a proper column name
                column_name = format_column_name(key_raw)

                # Store the value as string
                result[column_name] = str(value)
        else:
            # Not proper JSON, try escaped key-value format
            result = _parse_escaped_key_value_format(tag_string)

    except json.JSONDecodeError as e:
        logger.debug(f"Not valid JSON, trying escaped format: {e}")
        # If JSON parsing fails, try escaped key-value format
        result = _parse_escaped_key_value_format(tag_string)

    return result


def process_dataframe(df: pd.DataFrame, tag_column: str = None, date_value: str = None) -> pd.DataFrame:
    """
    Process a DataFrame by parsing the Tags column and dynamically adding ALL extracted columns.

    This function extracts ALL key-value pairs from the tags and creates a column for each unique key.

    Args:
        df: Input DataFrame
        tag_column: Name of the tags column (default from config)
        date_value: Date string (YYYY-MM format) to add to all rows

    Returns:
        DataFrame with dynamically added columns based on tags content + Date column

    Example:
        If tags contain ["primarycontact":"john", "usage":"databricks"],
        the result will have columns: "Primary Contact", "Usage", "Date"
    """
    if tag_column is None:
        tag_column = config.TAG_COLUMN

    # Validate that the tag column exists
    if tag_column not in list(df.columns):
        raise ValueError(f"Column '{tag_column}' not found in DataFrame. Available columns: {df.columns.tolist()}")

    logger.info(f"Processing {len(df)} rows with date value: {date_value}")

    # Parse tags for each row (vectorized operation)
    parsed_data = df[tag_column].apply(parse_tags)

    # Convert list of dictionaries to DataFrame
    # This will automatically create columns for ALL unique keys found
    parsed_df = pd.DataFrame(parsed_data.tolist())

    # Add Date column with the extracted date value
    parsed_df['Date'] = date_value

    # Check for duplicate columns and drop them from parsed_df
    # We want to keep the original Excel columns, not the parsed ones if they conflict
    duplicate_cols = [col for col in parsed_df.columns if col in df.columns and col != tag_column]
    if duplicate_cols:
        logger.warning(f"Dropping duplicate columns from parsed data (keeping original): {duplicate_cols}")
        parsed_df = parsed_df.drop(columns=duplicate_cols)

    # Add new columns to original DataFrame
    result_df = pd.concat([df, parsed_df], axis=1)

    # Log statistics about the parsed columns
    parsed_columns = [col for col in parsed_df.columns if col != 'Date']
    logger.info(f"Created {len(parsed_columns)} new columns from tags: {parsed_columns}")

    # Count non-null values for each parsed column
    for col in parsed_columns:
        count = int(parsed_df[col].notna().sum())
        if count > 0:
            logger.info(f"  - {col}: {count} rows with data")

    # Log date info
    if date_value:
        logger.info(f"Added Date column with value: {date_value}")

    return result_df
