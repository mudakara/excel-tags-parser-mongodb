"""
Excel file writing module for processed data with progress tracking
"""
import pandas as pd
import logging
from typing import List, Callable, Optional
import sys
import os
import xlsxwriter

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


def write_dataframe_to_excel_optimized(
    df: pd.DataFrame,
    output_path: str,
    sheet_name: str = 'Sheet1',
    batch_size: int = 5000,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> None:
    """
    Write DataFrame to Excel with optimized batch writing and real-time progress.

    Uses xlsxwriter engine which is 3-5x faster than openpyxl for writing.
    Writes data in batches to provide real-time progress feedback.

    Args:
        df: DataFrame to write
        output_path: Path where the Excel file will be saved
        sheet_name: Name of the worksheet (default: 'Sheet1')
        batch_size: Number of rows to write per batch (default: 5000)
        progress_callback: Optional callback function(rows_written, total_rows, message)

    Raises:
        IOError: If file cannot be written
    """
    if df is None or df.empty:
        raise ValueError("DataFrame is empty")

    total_rows = len(df)
    logger.info(f"Writing {total_rows:,} rows to {output_path} using xlsxwriter engine")

    try:
        # Create workbook with xlsxwriter
        workbook = xlsxwriter.Workbook(output_path, {'constant_memory': True})
        worksheet = workbook.add_worksheet(sheet_name)

        # Define formats for better performance
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1
        })

        # Write headers
        columns = df.columns.tolist()
        for col_idx, col_name in enumerate(columns):
            worksheet.write(0, col_idx, col_name, header_format)

        if progress_callback:
            progress_callback(0, total_rows, "Writing headers...")

        # Write data in batches
        rows_written = 0
        for start_idx in range(0, total_rows, batch_size):
            end_idx = min(start_idx + batch_size, total_rows)
            batch_df = df.iloc[start_idx:end_idx]

            # Write batch rows
            for batch_row_idx, (_, row) in enumerate(batch_df.iterrows()):
                excel_row = start_idx + batch_row_idx + 1  # +1 for header row
                for col_idx, col_name in enumerate(columns):
                    value = row[col_name]
                    # Handle NaN/None values
                    if pd.isna(value):
                        worksheet.write(excel_row, col_idx, '')
                    else:
                        worksheet.write(excel_row, col_idx, value)

            rows_written = end_idx

            # Report progress
            if progress_callback:
                progress_callback(
                    rows_written,
                    total_rows,
                    f"Writing rows {rows_written:,} / {total_rows:,} ({(rows_written/total_rows*100):.1f}%)"
                )

        # Close workbook
        workbook.close()

        if progress_callback:
            progress_callback(total_rows, total_rows, f"✅ Successfully wrote {total_rows:,} rows to Excel!")

        logger.info(f"Successfully wrote {total_rows:,} rows to {output_path}")

    except Exception as e:
        logger.error(f"Error writing Excel file: {e}")
        raise IOError(f"Failed to write Excel file: {e}")


def write_chunks_to_excel(
    chunks: List[pd.DataFrame],
    output_path: str,
    sheet_name: str = 'Sheet1',
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> None:
    """
    Write multiple DataFrame chunks to a single Excel file with progress tracking.

    This function concatenates all chunks and writes them to Excel with real-time progress.
    Use this when you've processed data in chunks.

    Args:
        chunks: List of DataFrame chunks to write
        output_path: Path where the Excel file will be saved
        sheet_name: Name of the worksheet (default: 'Sheet1')
        progress_callback: Optional callback function(rows_written, total_rows, message)
                          to report progress

    Raises:
        ValueError: If chunks list is empty
        IOError: If file cannot be written
    """
    if not chunks:
        raise ValueError("No chunks provided to write")

    logger.info(f"Combining {len(chunks)} chunks for writing")

    try:
        # Concatenate all chunks
        if progress_callback:
            progress_callback(0, 100, f"Combining {len(chunks)} chunks...")

        combined_df = pd.concat(chunks, ignore_index=True)
        total_rows = len(combined_df)
        logger.info(f"Combined {total_rows:,} total rows")

        if progress_callback:
            progress_callback(10, 100, f"Combined {total_rows:,} rows, starting write...")

        # Write to Excel with optimized batch writing
        # Wrap the progress callback to convert row-based progress to percentage
        def row_progress_callback(rows_written, total, message):
            # Map rows_written to 10-100% range (0-10% was combining)
            progress_pct = 10 + int((rows_written / total) * 90)
            if progress_callback:
                progress_callback(progress_pct, 100, message)

        write_dataframe_to_excel_optimized(
            combined_df,
            output_path,
            sheet_name,
            batch_size=5000,
            progress_callback=row_progress_callback
        )

        if progress_callback:
            progress_callback(100, 100, "Excel file created successfully!")

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
