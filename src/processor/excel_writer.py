"""
Excel file writing module for processed data
"""
import pandas as pd
import logging
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config

logger = logging.getLogger(__name__)


def write_to_excel(
    df: pd.DataFrame,
    output_path: str,
    sheet_name: str = 'Sheet1',
    index: bool = False
) -> None:
    """
    Write DataFrame to Excel file with optimization for large files.

    Args:
        df: DataFrame to write
        output_path: Path where the Excel file will be saved
        sheet_name: Name of the worksheet (default: 'Sheet1')
        index: Whether to include the DataFrame index (default: False)

    Raises:
        IOError: If file cannot be written
    """
    logger.info(f"Writing {len(df)} rows to {output_path}")

    try:
        # Use openpyxl engine for .xlsx files
        df.to_excel(
            output_path,
            sheet_name=sheet_name,
            index=index,
            engine='openpyxl'
        )
        logger.info(f"Successfully wrote file to {output_path}")

    except Exception as e:
        logger.error(f"Error writing Excel file: {e}")
        raise IOError(f"Failed to write Excel file: {e}")


def write_chunks_to_excel(
    chunks: List[pd.DataFrame],
    output_path: str,
    sheet_name: str = 'Sheet1'
) -> None:
    """
    Write multiple DataFrame chunks to a single Excel file.

    This function concatenates all chunks and writes them to Excel.
    Use this when you've processed data in chunks.

    Args:
        chunks: List of DataFrame chunks to write
        output_path: Path where the Excel file will be saved
        sheet_name: Name of the worksheet (default: 'Sheet1')

    Raises:
        ValueError: If chunks list is empty
        IOError: If file cannot be written
    """
    if not chunks:
        raise ValueError("No chunks provided to write")

    logger.info(f"Combining {len(chunks)} chunks for writing")

    try:
        # Concatenate all chunks
        combined_df = pd.concat(chunks, ignore_index=True)

        # Write to Excel
        write_to_excel(combined_df, output_path, sheet_name)

    except Exception as e:
        logger.error(f"Error writing chunks to Excel: {e}")
        raise


def append_to_excel(
    df: pd.DataFrame,
    output_path: str,
    sheet_name: str = 'Sheet1'
) -> None:
    """
    Append DataFrame to an existing Excel file.

    Args:
        df: DataFrame to append
        output_path: Path to the existing Excel file
        sheet_name: Name of the worksheet to append to

    Note:
        This creates a new file if it doesn't exist
    """
    logger.info(f"Appending {len(df)} rows to {output_path}")

    try:
        # Check if file exists
        if os.path.exists(output_path):
            # Read existing data
            existing_df = pd.read_excel(output_path, sheet_name=sheet_name)
            # Combine with new data
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            # Write back
            write_to_excel(combined_df, output_path, sheet_name)
        else:
            # File doesn't exist, create new
            write_to_excel(df, output_path, sheet_name)

    except Exception as e:
        logger.error(f"Error appending to Excel file: {e}")
        raise
