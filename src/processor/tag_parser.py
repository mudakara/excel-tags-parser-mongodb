"""
Tag parsing module for extracting Application Name, Environment, and Owner from Tags column
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


def parse_tags(tag_string: Any) -> Dict[str, str]:
    """
    Parse tags column and extract application, environment, owner, and cost information.

    Supports multiple tag formats:
    1. Escaped JSON: "\"owner\":\"data\",\"environment\":\"production\",\"applicationname\":\"arcesb\",\"cost\":\"1000\""
    2. Key-value pairs: "applicationname:myapp,environment:prod,owner:john,cost:500"
    3. JSON format: '{"applicationname": "myapp", "environment": "prod", "owner": "john", "cost": "1000"}'
    4. Pipe-separated values (ordered): "myapp|prod|john|1000"

    STRICT FIELD MATCHING:
    - Application Name: Only from "applicationname" or "application_name" (not "app" or "application")
    - Environment: Only from "environment" (not "env")
    - Owner: Only from "owner"
    - Cost: Only from "cost"

    Args:
        tag_string: The tag string to parse (from Tags column)

    Returns:
        Dictionary with keys: 'Application Name', 'Environment', 'Owner', 'Cost'
        Returns None for each key if not found

    Examples:
        >>> parse_tags('"owner":"data","environment":"production","applicationname":"arcesb","cost":"1000"')
        {'Application Name': 'arcesb', 'Environment': 'production', 'Owner': 'data', 'Cost': '1000'}

        >>> parse_tags("myapp|production|john|1000")
        {'Application Name': 'myapp', 'Environment': 'production', 'Owner': 'john', 'Cost': '1000'}
    """
    result = {
        'Application Name': None,
        'Environment': None,
        'Owner': None,
        'Cost': None
    }

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
            # If JSON parsing didn't extract anything, try other methods
            if result['Application Name'] is None and result['Environment'] is None and result['Owner'] is None and result['Cost'] is None:
                result = _parse_escaped_key_value_format(tag_string)

        # Strategy 2: Key-value pairs (most common format)
        elif ':' in tag_string:
            result = _parse_key_value_format(tag_string)

        # Strategy 3: Pipe-separated ordered values
        elif '|' in tag_string:
            result = _parse_pipe_separated_format(tag_string)

        # Strategy 4: Custom pattern matching (can be extended)
        else:
            logger.debug(f"No matching format for tag: {tag_string}")

    except Exception as e:
        logger.warning(f"Error parsing tag '{tag_string}': {e}")

    return result


def _parse_escaped_key_value_format(tag_string: str) -> Dict[str, str]:
    """
    Parse escaped JSON key-value format tags.

    Format: "owner":"data","environment":"production","applicationname":"arcesb","cost":"1000"
    """
    result = {
        'Application Name': None,
        'Environment': None,
        'Owner': None,
        'Cost': None
    }

    # Use regex to extract quoted key-value pairs
    # Pattern: "key":"value"
    pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
    matches = re.findall(pattern, tag_string)

    for key, value in matches:
        key_lower = key.strip().lower()
        value_clean = value.strip()

        # Map key names to standard fields - STRICT matching for applicationname only
        if key_lower in ['applicationname', 'application_name']:
            result['Application Name'] = value_clean
        elif key_lower in ['environment']:
            result['Environment'] = value_clean
        elif key_lower in ['owner']:
            result['Owner'] = value_clean
        elif key_lower in ['cost']:
            result['Cost'] = value_clean

    return result


def _parse_key_value_format(tag_string: str) -> Dict[str, str]:
    """
    Parse key-value format tags.

    Formats: "applicationname:myapp,environment:prod,owner:john,cost:500"
    """
    result = {
        'Application Name': None,
        'Environment': None,
        'Owner': None,
        'Cost': None
    }

    # Split by common separators
    pairs = re.split(r'[,;|]', tag_string)

    for pair in pairs:
        pair = pair.strip()
        if ':' not in pair:
            continue

        try:
            key, value = pair.split(':', 1)
            key = key.strip().lower()
            value = value.strip()

            # Remove surrounding quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            # Map key names to standard fields - STRICT matching for applicationname only
            if key in ['applicationname', 'application_name']:
                result['Application Name'] = value
            elif key in ['environment']:
                result['Environment'] = value
            elif key in ['owner']:
                result['Owner'] = value
            elif key in ['cost']:
                result['Cost'] = value

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
    Parse JSON-like format tags.

    Format: '{"applicationname": "myapp", "environment": "prod", "owner": "john", "cost": "1000"}'
    """
    import json

    result = {
        'Application Name': None,
        'Environment': None,
        'Owner': None,
        'Cost': None
    }

    try:
        # Try to parse as proper JSON first
        if tag_string.startswith('{') and tag_string.endswith('}'):
            data = json.loads(tag_string)

            # Map JSON keys to standard fields - STRICT matching for applicationname only
            for key, value in data.items():
                key_lower = key.lower()
                if key_lower in ['applicationname', 'application_name']:
                    result['Application Name'] = str(value)
                elif key_lower in ['environment']:
                    result['Environment'] = str(value)
                elif key_lower in ['owner']:
                    result['Owner'] = str(value)
                elif key_lower in ['cost']:
                    result['Cost'] = str(value)
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
    Process a DataFrame by parsing the Tags column and adding new columns.

    Args:
        df: Input DataFrame
        tag_column: Name of the tags column (default from config)
        date_value: Date string (YYYY-MM format) to add to all rows

    Returns:
        DataFrame with four new columns added: Application Name, Environment, Owner, Date
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
    parsed_df = pd.DataFrame(parsed_data.tolist())

    # Add Date column with the extracted date value
    parsed_df['Date'] = date_value

    # Remove Cost column from parsed_df if it exists in the original df
    # We want to use the actual Cost column from Excel, not from tags parsing
    if 'Cost' in df.columns and 'Cost' in parsed_df.columns:
        logger.info("Cost column exists in both original data and parsed tags - using original data")
        parsed_df = parsed_df.drop(columns=['Cost'])

    # Check for any other duplicate columns and drop them from parsed_df
    duplicate_cols = [col for col in parsed_df.columns if col in df.columns and col != tag_column]
    if duplicate_cols:
        logger.warning(f"Dropping duplicate columns from parsed data: {duplicate_cols}")
        parsed_df = parsed_df.drop(columns=duplicate_cols)

    # Add new columns to original DataFrame
    result_df = pd.concat([df, parsed_df], axis=1)

    # Log statistics
    app_count = int(parsed_df['Application Name'].notna().sum()) if 'Application Name' in parsed_df.columns else 0
    env_count = int(parsed_df['Environment'].notna().sum()) if 'Environment' in parsed_df.columns else 0
    owner_count = int(parsed_df['Owner'].notna().sum()) if 'Owner' in parsed_df.columns else 0

    # Check if Cost column exists in the final result (original df has it)
    if 'Cost' in result_df.columns:
        cost_count = int(result_df['Cost'].notna().sum())
    else:
        cost_count = 0

    logger.info(f"Parsed results - Application Name: {app_count}, Environment: {env_count}, Owner: {owner_count}, Cost: {cost_count}, Date: {date_value}")

    return result_df
