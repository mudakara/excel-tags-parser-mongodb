"""
Main application entry point for Excel Tags Parser

This module provides both CLI and programmatic interfaces for processing Excel files.
"""
import sys
import os
import logging
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config
from src.processor.excel_reader import read_excel_in_chunks
from src.processor.tag_parser import process_dataframe
from src.processor.excel_writer import write_chunks_to_excel
from src.utils.validators import validate_excel_file, validate_tag_column

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


def process_excel_file(
    input_path: str,
    output_path: str,
    progress_callback: Optional[callable] = None
) -> bool:
    """
    Process an Excel file by parsing Tags column and adding new columns.

    Args:
        input_path: Path to input Excel file
        output_path: Path where processed file will be saved
        progress_callback: Optional callback function(processed_rows, total_rows)

    Returns:
        True if successful, False otherwise

    Example:
        >>> def show_progress(processed, total):
        ...     print(f"Progress: {processed}/{total}")
        >>> process_excel_file('input.xlsx', 'output.xlsx', show_progress)
    """
    logger.info(f"Starting processing: {input_path} -> {output_path}")

    # Validate input file
    is_valid, error_msg = validate_excel_file(input_path)
    if not is_valid:
        logger.error(f"Validation failed: {error_msg}")
        return False

    try:
        processed_chunks = []
        total_processed = 0

        # Process file in chunks
        for chunk, total_rows in read_excel_in_chunks(input_path):
            # Process the chunk
            processed_chunk = process_dataframe(chunk)
            processed_chunks.append(processed_chunk)

            # Update progress
            total_processed += len(chunk)

            if progress_callback:
                progress_callback(total_processed, total_rows)

        # Write results
        logger.info(f"Writing {total_processed} rows to {output_path}")
        write_chunks_to_excel(processed_chunks, output_path)

        logger.info("Processing completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        return False


def main():
    """
    Command-line interface for the Excel Tags Parser.

    Usage:
        python src/app.py <input_file> <output_file>
    """
    if len(sys.argv) != 3:
        print("Excel Tags Parser - Command Line Interface")
        print()
        print("Usage:")
        print("  python src/app.py <input_file> <output_file>")
        print()
        print("Example:")
        print("  python src/app.py data/input.xlsx data/output.xlsx")
        print()
        print("For web interface, run:")
        print("  streamlit run src/ui/streamlit_app.py")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Progress callback
    def show_progress(processed, total):
        if total > 0:
            percentage = int((processed / total) * 100)
            print(f"\rProgress: {processed:,} / {total:,} rows ({percentage}%)", end='', flush=True)
        else:
            print(f"\rProcessing: {processed:,} rows", end='', flush=True)

    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()

    success = process_excel_file(input_file, output_file, show_progress)

    print()  # New line after progress
    if success:
        print("✓ Processing completed successfully!")
        print(f"Output saved to: {output_file}")
        sys.exit(0)
    else:
        print("✗ Processing failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
