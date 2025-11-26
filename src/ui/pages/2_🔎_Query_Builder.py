"""
Query Builder Page - Query MongoDB data with dynamic fields
"""
import streamlit as st
import pandas as pd
import os
import sys
import logging
from typing import Dict, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
import config
from src.database.mongodb_client import test_connection, get_collection
from src.database.mongodb_operations import get_statistics

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Query Builder",
    page_icon="🔎",
    layout="wide"
)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_available_fields() -> Dict:
    """Get all available queryable fields from MongoDB (cached)"""
    try:
        collection = get_collection()
        sample_doc = collection.find_one()

        if not sample_doc:
            return {
                "standard_fields": [],
                "dynamic_fields": [],
                "all_fields": []
            }

        system_fields = ['_id', 'tags', 'originalData', 'metadata']
        standard = ['applicationName', 'environment', 'owner', 'cost', 'date']

        all_fields = []
        dynamic_fields = []

        for field in sample_doc.keys():
            if field not in system_fields:
                all_fields.append(field)
                if field not in standard:
                    dynamic_fields.append(field)

        return {
            "standard_fields": [f for f in standard if f in all_fields],
            "dynamic_fields": dynamic_fields,
            "all_fields": all_fields
        }
    except Exception as e:
        logger.error(f"Error getting available fields: {e}")
        return {
            "standard_fields": [],
            "dynamic_fields": [],
            "all_fields": []
        }


def advanced_query(filters: Dict, limit: int = 100) -> Dict:
    """Query MongoDB with any combination of fields and return total count"""
    try:
        collection = get_collection()
        # Get total count of matching documents
        total_count = collection.count_documents(filters)
        # Get limited results
        results = list(collection.find(filters).limit(limit))
        return {
            "results": results,
            "total_count": total_count,
            "displayed_count": len(results)
        }
    except Exception as e:
        logger.error(f"Error in advanced query: {e}")
        return {
            "results": [],
            "total_count": 0,
            "displayed_count": 0
        }


def create_recommended_indexes():
    """Create recommended MongoDB indexes for better performance"""
    try:
        collection = get_collection()

        # Create indexes on frequently queried fields
        indexes_created = []

        # Index on applicationName
        collection.create_index("applicationName")
        indexes_created.append("applicationName")

        # Index on environment
        collection.create_index("environment")
        indexes_created.append("environment")

        # Index on owner
        collection.create_index("owner")
        indexes_created.append("owner")

        # Index on date
        collection.create_index("date")
        indexes_created.append("date")

        # Compound index for cost analysis queries
        collection.create_index([("applicationName", 1), ("environment", 1), ("date", 1)])
        indexes_created.append("applicationName + environment + date (compound)")

        return indexes_created
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        return []


def check_existing_indexes() -> List[str]:
    """Check which indexes already exist"""
    try:
        collection = get_collection()
        indexes = collection.list_indexes()
        index_names = [idx['name'] for idx in indexes if idx['name'] != '_id_']
        return index_names
    except Exception as e:
        logger.error(f"Error checking indexes: {e}")
        return []


def main():
    """Main query builder page function"""

    st.title("🔎 Query Builder")
    st.markdown("""
    Query your data using **all dynamically extracted fields**.
    Build custom queries with any combination of filters.
    """)

    # Test MongoDB connection
    if not test_connection():
        st.error("❌ Cannot connect to MongoDB. Please check if MongoDB is running on localhost:27017")
        st.info("To start MongoDB, run: `mongod` or `brew services start mongodb-community`")
        return

    # Get available fields
    fields_data = get_available_fields()

    if not fields_data["all_fields"]:
        st.warning("⚠️ No data found in MongoDB. Please upload and process an Excel file first.")
        st.info("Go to the **Excel Upload** page to upload data.")
        return

    # Sidebar - Field Explorer
    with st.sidebar:
        st.header("🔍 Field Explorer")

        st.markdown("**Standard Fields:**")
        for field in fields_data["standard_fields"]:
            st.markdown(f"- `{field}`")

        if fields_data["dynamic_fields"]:
            st.markdown("**Dynamic Fields:**")
            for field in fields_data["dynamic_fields"]:
                st.markdown(f"- `{field}`")

        st.markdown("---")

        # Performance Optimization Section
        with st.expander("⚡ Performance Optimization"):
            st.markdown("**Database Indexes**")
            st.caption("Indexes speed up queries on large datasets")

            existing_indexes = check_existing_indexes()

            if existing_indexes:
                st.success(f"✅ {len(existing_indexes)} indexes found")
                with st.expander("View Indexes"):
                    for idx in existing_indexes:
                        st.text(f"• {idx}")
            else:
                st.warning("⚠️ No indexes found")

            if st.button("🚀 Create Recommended Indexes", help="Creates indexes on frequently queried fields"):
                with st.spinner("Creating indexes..."):
                    created = create_recommended_indexes()
                    if created:
                        st.success(f"✅ Created {len(created)} indexes!")
                        for idx in created:
                            st.text(f"✓ {idx}")
                        st.info("💡 Refresh the page to see performance improvements")
                    else:
                        st.error("Failed to create indexes")

            st.markdown("---")
            st.markdown("**Cache Status**")
            if st.button("🗑️ Clear Cache", help="Clear cached data to reload fresh values"):
                st.cache_data.clear()
                st.success("✅ Cache cleared!")
                st.info("Refresh the page to reload data")

        st.markdown("---")

        # Database stats - Lazy load on demand
        if st.checkbox("Show Database Stats", value=False):
            with st.spinner("Loading stats..."):
                try:
                    stats = get_statistics()
                    if stats:
                        st.markdown("**Database Overview:**")
                        st.metric("Total Documents", f"{stats.get('total_documents', 0):,}")
                        st.metric("Unique Apps", f"{stats.get('unique_applications', 0):,}")
                        st.metric("Unique Envs", f"{stats.get('unique_environments', 0):,}")
                except Exception as e:
                    logger.warning(f"Could not load stats: {e}")
                    st.error("Failed to load statistics")

    # Main content
    st.markdown("---")
    st.subheader("🔎 Build Your Query")
    st.markdown("Add filters to search your data using any combination of fields.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Add Filters:**")

        # Dynamic filter builder
        if 'query_filters' not in st.session_state:
            st.session_state.query_filters = {}

        filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])

        with filter_col1:
            filter_field = st.selectbox(
                "Field",
                options=fields_data["all_fields"],
                key="filter_field"
            )

        with filter_col2:
            filter_value = st.text_input(
                "Value",
                key="filter_value"
            )

        with filter_col3:
            # Add label space to align button with input fields (adjusted 5px up)
            st.markdown("<div style='margin-bottom: 3px;'>&nbsp;</div>", unsafe_allow_html=True)
            if st.button("➕ Add", key="add_filter", use_container_width=True):
                if filter_field and filter_value:
                    st.session_state.query_filters[filter_field] = filter_value
                    st.rerun()

        # Show current filters
        if st.session_state.query_filters:
            st.markdown("**Current Filters:**")
            for field, value in st.session_state.query_filters.items():
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.code(f"{field} = {value}")
                with col_b:
                    if st.button("❌", key=f"remove_{field}"):
                        del st.session_state.query_filters[field]
                        st.rerun()

    with col2:
        # Add spacing to align with filter input fields (match "Add Filters:" label height)
        st.markdown("&nbsp;")
        result_limit = st.number_input(
            "Max Results",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        )

    if st.button("🔍 Run Query", type="primary", use_container_width=True):
        if not st.session_state.query_filters:
            st.warning("⚠️ Please add at least one filter")
        else:
            with st.spinner("Querying..."):
                query_result = advanced_query(st.session_state.query_filters, result_limit)

                if query_result["total_count"] > 0:
                    # Display total count and showing info
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.metric("Total Matching Records", f"{query_result['total_count']:,}")
                    with col_info2:
                        st.metric("Displaying", f"{query_result['displayed_count']:,} records")

                    if query_result['total_count'] > query_result['displayed_count']:
                        st.info(f"ℹ️ Showing {query_result['displayed_count']} of {query_result['total_count']:,} total results. Increase 'Max Results' to see more.")

                    # Convert to DataFrame for display
                    df = pd.DataFrame(query_result["results"])
                    if '_id' in df.columns:
                        df = df.drop('_id', axis=1)
                    if 'tags' in df.columns:
                        df = df.drop('tags', axis=1)
                    if 'originalData' in df.columns:
                        df = df.drop('originalData', axis=1)
                    if 'metadata' in df.columns:
                        df = df.drop('metadata', axis=1)

                    st.dataframe(df, use_container_width=True)

                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="query_results.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No results found matching your filters")


if __name__ == "__main__":
    main()
