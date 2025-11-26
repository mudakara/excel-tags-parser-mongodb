"""
Excel Upload Page - Upload and process Excel files with tag parsing
"""
import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
import config
from src.processor.excel_reader import read_excel_in_chunks, extract_start_date_from_summary
from src.processor.tag_parser import process_dataframe
from src.processor.excel_writer import write_chunks_to_excel
from src.utils.validators import validate_uploaded_file, validate_tag_column, validate_tag_column_in_file
from src.database.mongodb_client import test_connection
from src.database.mongodb_operations import insert_dataframe_to_mongodb, get_statistics

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Excel Upload - Tags Parser",
    page_icon="📤",
    layout="wide"
)


def main():
    """Main Excel upload page function"""

    # Title and description
    st.title("📤 Excel Upload & Processing")
    st.markdown("""
    Upload an Excel file to automatically extract **ALL fields** from the Tags column.
    This tool is optimized to handle large files with 100,000+ rows.

    **Expected Excel Structure:**
    - **Summary sheet**: Must contain "Start date:" with a date value (extracted as YYYY-MM)
    - **Data sheet**: Contains the actual data to be processed
    - **Tags column**: Contains key-value pairs to be extracted
    """)

    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ Information")
        st.markdown(f"""
        **Supported Formats:**
        - File Types: {', '.join(config.ALLOWED_EXTENSIONS)}
        - Max File Size: {config.MAX_FILE_SIZE_MB} MB
        - Required Column: `{config.TAG_COLUMN}`

        **Tag Formats Supported:**
        1. Escaped JSON:
           - `"key1":"value1","key2":"value2"`
        2. Key-value pairs:
           - `key1:value1,key2:value2`
        3. JSON format:
           - `{{"key1":"value1","key2":"value2"}}`
        4. Pipe-separated (limited):
           - `value1|value2|value3`
        """)

        st.markdown("---")
        st.markdown("**Processing Settings:**")
        st.markdown(f"- Chunk Size: {config.CHUNK_SIZE:,} rows")
        st.markdown(f"- Parallel Processing: {'Enabled' if config.ENABLE_PARALLEL_PROCESSING else 'Disabled'}")

        st.markdown("---")
        st.markdown("**MongoDB Settings:**")
        st.markdown(f"- Database: `{config.MONGODB_DATABASE}`")
        st.markdown(f"- Collection: `{config.MONGODB_COLLECTION}`")

        # Test MongoDB connection
        if st.button("Test MongoDB Connection"):
            with st.spinner("Testing connection..."):
                if test_connection():
                    st.success("✅ Connected to MongoDB")
                else:
                    st.error("❌ Cannot connect to MongoDB")

    # Initialize session state
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'processed_df' not in st.session_state:
        st.session_state.processed_df = None
    if 'processed_filename' not in st.session_state:
        st.session_state.processed_filename = None
    if 'extracted_date' not in st.session_state:
        st.session_state.extracted_date = None

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help=f"Upload an Excel file (max {config.MAX_FILE_SIZE_MB} MB)"
    )

    if uploaded_file is not None:
        # Validate uploaded file
        is_valid, error_msg = validate_uploaded_file(uploaded_file)

        if not is_valid:
            st.error(f"❌ {error_msg}")
            return

        # Display file information
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"✅ File uploaded: **{uploaded_file.name}**")
        with col2:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"📁 File size: **{file_size_mb:.2f} MB**")

        # Save uploaded file temporarily
        upload_path = os.path.join(config.UPLOAD_DIR, uploaded_file.name)
        with open(upload_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Extract date from Summary sheet
        try:
            extracted_date = extract_start_date_from_summary(upload_path)
            if extracted_date:
                st.session_state.extracted_date = extracted_date
                st.success(f"📅 Extracted Date from Summary sheet: **{extracted_date}**")
            else:
                st.warning("⚠️ Could not extract date from Summary sheet. Will process without date.")
                st.session_state.extracted_date = None
        except Exception as e:
            st.warning(f"⚠️ Error extracting date from Summary sheet: {str(e)}")
            st.session_state.extracted_date = None

        # Preview the file (from Data sheet)
        try:
            preview_df = pd.read_excel(upload_path, sheet_name='Data', nrows=5, engine='openpyxl')

            st.subheader("📋 File Preview from Data sheet (first 5 rows)")
            st.dataframe(preview_df, use_container_width=True)

            # Check if Tags column exists in preview
            is_valid, error_msg = validate_tag_column(preview_df)
            if not is_valid:
                st.error(f"❌ {error_msg}")
                st.info(f"Available columns: {', '.join(preview_df.columns.tolist())}")
                os.remove(upload_path)
                return

        except Exception as e:
            st.error(f"❌ Error reading Data sheet: {str(e)}")
            st.info("Make sure your Excel file has a 'Data' sheet with the required columns.")
            if os.path.exists(upload_path):
                os.remove(upload_path)
            return

        # Validate Tags column has data in the full file
        with st.spinner("🔍 Validating Tags column in full file..."):
            try:
                is_valid, error_msg, stats = validate_tag_column_in_file(
                    upload_path,
                    sheet_name='Data',
                    sample_size=10000
                )

                if not is_valid:
                    st.error(f"❌ {error_msg}")
                    if stats:
                        st.info(f"Checked {stats.get('total_rows', 0)} rows - all Tags were empty")
                    os.remove(upload_path)
                    return

                if stats and stats.get('non_empty_rows', 0) > 0:
                    non_empty = stats['non_empty_rows']
                    total = stats['total_rows']
                    percentage = (non_empty / total * 100) if total > 0 else 0
                    st.success(f"✅ Tags column validated: {non_empty:,}/{total:,} rows ({percentage:.1f}%) have data")

            except Exception as e:
                st.warning(f"⚠️ Could not fully validate Tags column: {str(e)}")
                st.info("Will proceed with processing - validation will occur during processing")

        # Process button
        st.markdown("---")
        process_button = st.button("🚀 Process File", type="primary", use_container_width=True)

        if process_button:
            st.session_state.processing_complete = False
            process_file(upload_path, uploaded_file.name)

    # Show MongoDB push button at the END of the page if processing is complete
    if st.session_state.processing_complete and st.session_state.processed_df is not None:
        st.markdown("---")
        st.markdown("---")  # Extra separator for visual distinction
        st.subheader("📤 Push to Database")

        col1, col2 = st.columns([1, 1])
        with col1:
            st.info(f"**Ready to push:** {len(st.session_state.processed_df):,} rows")

        with col2:
            push_button = st.button("📤 Push to MongoDB", type="primary", use_container_width=True, key="push_mongodb_btn")

        # Create placeholders for progress (these will be filled when button is clicked)
        mongodb_separator = st.empty()
        mongodb_header = st.empty()
        mongodb_status_placeholder = st.empty()
        mongodb_progress_bar = st.empty()
        mongodb_status_text = st.empty()
        mongodb_result_placeholder = st.empty()

        if push_button:
            push_to_mongodb(
                st.session_state.processed_df,
                st.session_state.processed_filename,
                mongodb_separator,
                mongodb_header,
                mongodb_status_placeholder,
                mongodb_progress_bar,
                mongodb_status_text,
                mongodb_result_placeholder
            )


def process_file(upload_path: str, original_filename: str):
    """Process the uploaded Excel file"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    stats_placeholder = st.empty()

    try:
        date_value = st.session_state.get('extracted_date', None)

        status_text.text("🔄 Initializing processing from Data sheet...")
        processed_chunks = []
        total_processed = 0
        total_rows_estimate = 0

        chunk_count = 0
        for chunk, total_rows in read_excel_in_chunks(upload_path, sheet_name='Data'):
            chunk_count += 1
            total_rows_estimate = total_rows if total_rows > 0 else total_processed

            status_text.text(f"🔄 Processing chunk {chunk_count} from Data sheet...")
            processed_chunk = process_dataframe(chunk, date_value=date_value)
            processed_chunks.append(processed_chunk)

            total_processed += len(chunk)
            if total_rows_estimate > 0:
                progress = min(int((total_processed / total_rows_estimate) * 100), 100)
            else:
                progress = 50

            progress_bar.progress(progress)
            status_text.text(f"⏳ Processing: {total_processed:,} rows processed...")

            with stats_placeholder.container():
                col1, col2, col3 = st.columns(3)
                col1.metric("Rows Processed", f"{total_processed:,}")
                col2.metric("Chunks Processed", chunk_count)
                if total_rows_estimate > 0:
                    col3.metric("Progress", f"{progress}%")

        status_text.text("🔄 Combining chunks...")
        final_df = pd.concat(processed_chunks, ignore_index=True)

        timestamp = datetime.now().strftime(config.OUTPUT_FILENAME_TIMESTAMP_FORMAT)
        output_filename = f"{config.OUTPUT_FILENAME_PREFIX}{timestamp}_{original_filename}"
        output_path = os.path.join(config.PROCESSED_DIR, output_filename)

        st.markdown("---")
        st.subheader("💾 Writing to Excel File")

        excel_progress_bar = st.progress(0)
        excel_status_text = st.empty()
        excel_metrics_placeholder = st.empty()

        def excel_progress_callback(current_step, total_steps, message):
            progress_pct = int((current_step / total_steps) * 100) if total_steps > 0 else 0
            excel_progress_bar.progress(progress_pct)
            excel_status_text.text(message)

            # Show real-time metrics during writing
            if "Writing rows" in message:
                with excel_metrics_placeholder.container():
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Progress", f"{progress_pct}%")
                    col2.metric("Status", "Writing...")
                    # Extract row count from message if available
                    if "/" in message:
                        try:
                            parts = message.split("rows")[1].strip().split("/")
                            if len(parts) >= 2:
                                current = parts[0].strip().replace(",", "")
                                total = parts[1].strip().split("(")[0].strip().replace(",", "")
                                col3.metric("Rows Written", f"{current} / {total}")
                        except:
                            col3.metric("Status", "Processing...")

        write_chunks_to_excel(processed_chunks, output_path, progress_callback=excel_progress_callback)

        excel_progress_bar.progress(100)
        excel_status_text.text("")
        excel_metrics_placeholder.empty()
        progress_bar.progress(100)
        status_text.text("")

        st.success(f"✅ Processing complete! Processed {total_processed:,} rows")

        # Show statistics
        st.subheader("📊 Processing Statistics")
        col1, col2, col3, col4, col5 = st.columns(5)

        app_count = int(final_df['Application Name'].notna().sum()) if 'Application Name' in final_df.columns else 0
        env_count = int(final_df['Environment'].notna().sum()) if 'Environment' in final_df.columns else 0
        owner_count = int(final_df['Owner'].notna().sum()) if 'Owner' in final_df.columns else 0
        cost_count = int(final_df['Cost'].notna().sum()) if 'Cost' in final_df.columns else 0
        date_count = int(final_df['Date'].notna().sum()) if 'Date' in final_df.columns else 0

        with col1:
            st.metric("Total Rows", f"{len(final_df):,}")
        with col2:
            st.metric("Application Names", f"{app_count:,}")
        with col3:
            st.metric("Environments", f"{env_count:,}")
        with col4:
            st.metric("Owners", f"{owner_count:,}")
        with col5:
            st.metric("Dates Added", f"{date_count:,}")

        if date_value is not None and str(date_value).strip():
            st.info(f"📅 Date added to all rows: **{date_value}**")
        if cost_count > 0:
            st.info(f"💰 Cost values found: **{cost_count:,}** rows")

        # Show preview
        st.subheader("👀 Results Preview (first 100 rows)")
        preview_columns = [config.TAG_COLUMN, 'Application Name', 'Environment', 'Owner', 'Cost', 'Date']
        available_preview_cols = [col for col in preview_columns if col in list(final_df.columns)]

        if available_preview_cols:
            st.dataframe(final_df[available_preview_cols].head(100), use_container_width=True)
        else:
            st.warning("No preview columns available to display")

        st.session_state['processed_df'] = final_df
        st.session_state['processed_filename'] = original_filename
        st.session_state['processing_complete'] = True

        # Download button
        st.markdown("---")
        with open(output_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Processed File",
                data=f,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )

        # Show sample of parsed values
        with st.expander("🔍 View Sample Parsed Values"):
            sample_size = min(20, len(final_df))
            if available_preview_cols and 'Application Name' in final_df.columns:
                filtered_df = final_df[final_df['Application Name'].notna()]
                if not filtered_df.empty:
                    sample_df = filtered_df[available_preview_cols].head(sample_size)
                    st.dataframe(sample_df, use_container_width=True)
                else:
                    st.warning("No rows with parsed Application Name found")
            else:
                st.warning("Cannot show sample - required columns not available")

    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please check that your file format is correct and try again.")

    finally:
        if os.path.exists(upload_path):
            try:
                os.remove(upload_path)
                logger.info(f"Cleaned up temporary file: {upload_path}")
            except Exception as e:
                logger.warning(f"Could not remove temporary file: {e}")


def push_to_mongodb(
    df: pd.DataFrame,
    source_filename: str,
    separator_placeholder,
    header_placeholder,
    status_placeholder,
    progress_placeholder,
    status_text_placeholder,
    result_placeholder
):
    """Push processed DataFrame to MongoDB"""
    # Use the provided placeholders
    separator_placeholder.markdown("---")
    header_placeholder.subheader("📤 Pushing to MongoDB")

    status_placeholder.info("🔄 Testing MongoDB connection...")

    if not test_connection():
        status_placeholder.error("❌ Cannot connect to MongoDB. Please check if MongoDB is running on localhost:27017")
        result_placeholder.info("To start MongoDB, run: `mongod` or `brew services start mongodb-community`")
        return

    status_placeholder.success("✅ Connected to MongoDB")

    def mongodb_progress_callback(current, total, message):
        progress_pct = int((current / total) * 100) if total > 0 else 0
        progress_placeholder.progress(progress_pct)
        status_text_placeholder.text(message)

    try:
        result = insert_dataframe_to_mongodb(
            df,
            source_file=source_filename,
            progress_callback=mongodb_progress_callback
        )

        progress_placeholder.progress(100)
        status_text_placeholder.text("")

        if result['success']:
            # Build success message with statistics
            with result_placeholder.container():
                st.success(f"✅ Successfully inserted {result['inserted']:,} documents into MongoDB!")

                st.markdown("### 📊 Insertion Statistics")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Documents", f"{result['total_documents']:,}")
                with col2:
                    st.metric("Inserted", f"{result['inserted']:,}")
                with col3:
                    st.metric("Failed", f"{result['failed']:,}")
                with col4:
                    success_rate = (result['inserted'] / result['total_documents'] * 100) if result['total_documents'] > 0 else 0
                    st.metric("Success Rate", f"{success_rate:.1f}%")

                st.info(f"**Database:** `{result['database']}` | **Collection:** `{result['collection']}`")

                try:
                    stats = get_statistics()
                    if stats:
                        with st.expander("📊 View Database Statistics"):
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                st.metric("Total Documents in DB", f"{stats['total_documents']:,}")
                            with col2:
                                st.metric("Unique Applications", f"{stats['unique_applications']:,}")
                            with col3:
                                st.metric("Unique Environments", f"{stats['unique_environments']:,}")
                            with col4:
                                st.metric("Unique Owners", f"{stats['unique_owners']:,}")

                            st.markdown("**Applications:**")
                            st.write(", ".join([str(app) for app in stats['applications'] if app]))

                            st.markdown("**Environments:**")
                            st.write(", ".join([str(env) for env in stats['environments'] if env]))

                            st.markdown("**Owners:**")
                            st.write(", ".join([str(owner) for owner in stats['owners'] if owner]))

                except Exception as e:
                    logger.warning(f"Could not retrieve statistics: {e}")

        else:
            with result_placeholder.container():
                st.error(f"❌ Error inserting data: {result.get('error', 'Unknown error')}")
                st.info(f"Inserted: {result['inserted']}, Failed: {result['failed']}")

    except Exception as e:
        logger.error(f"Error pushing to MongoDB: {e}", exc_info=True)
        with result_placeholder.container():
            st.error(f"❌ Error: {str(e)}")
            st.info("Please check that MongoDB is running and accessible.")


if __name__ == "__main__":
    main()
