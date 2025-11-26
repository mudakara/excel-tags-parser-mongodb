"""
Monthly Cost Comparison - Compare monthly costs for selected applications over a custom date range
"""
import streamlit as st
import pandas as pd
import os
import sys
import logging
import plotly.graph_objects as go
from typing import Dict, List
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
import config
from src.database.mongodb_client import test_connection, get_collection

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Monthly Comparison",
    page_icon="📈",
    layout="wide"
)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_all_application_names() -> List[str]:
    """
    Get list of all unique application names from the database.

    This is MUCH faster than aggregation because:
    - Uses MongoDB's distinct() method (optimized for this use case)
    - No date filtering (returns all applications ever recorded)
    - No cost calculations or conversions
    - Works directly with indexes if they exist
    """
    try:
        collection = get_collection()

        # Use distinct() - fastest way to get unique values
        # This uses indexes if available and doesn't scan all documents
        applications = collection.distinct("applicationName")

        # Filter out None/empty values and sort
        app_list = [app for app in applications if app and str(app).strip()]
        app_list.sort()  # Sort alphabetically

        logger.info(f"Retrieved {len(app_list)} unique application names")
        return app_list

    except Exception as e:
        logger.error(f"Error getting application names: {e}")
        return []


def get_monthly_cost_by_applications(applications: List[str], start_date: str, end_date: str) -> List[Dict]:
    """Get monthly cost breakdown for multiple applications"""
    try:
        collection = get_collection()

        pipeline = [
            {
                "$match": {
                    "applicationName": {"$in": applications},
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {"$project": {"applicationName": 1, "cost": 1, "date": 1}},
            {
                "$addFields": {
                    "numericCost": {
                        "$convert": {
                            "input": "$cost",
                            "to": "double",
                            "onError": 0,
                            "onNull": 0
                        }
                    },
                    "yearMonth": {"$substr": ["$date", 0, 7]}
                }
            },
            {
                "$group": {
                    "_id": {
                        "application": "$applicationName",
                        "month": "$yearMonth"
                    },
                    "totalCost": {"$sum": "$numericCost"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.month": 1, "_id.application": 1}}
        ]

        results = list(collection.aggregate(pipeline, allowDiskUse=True))

        # Format results
        formatted_results = []
        for r in results:
            formatted_results.append({
                "application": r["_id"]["application"],
                "month": r["_id"]["month"],
                "total_cost": round(r["totalCost"], 2),
                "count": r["count"]
            })

        return formatted_results
    except Exception as e:
        logger.error(f"Error getting monthly cost by applications: {e}")
        return []


def main():
    """Main monthly comparison page"""

    st.title("📈 Monthly Cost Comparison")
    st.markdown("Compare monthly costs for selected applications over a custom date range.")

    # Test MongoDB connection
    if not test_connection():
        st.error("❌ Cannot connect to MongoDB. Please check if MongoDB is running on localhost:27017")
        st.info("To start MongoDB, run: `mongod` or `brew services start mongodb-community`")
        return

    st.markdown("---")

    # Lazy load applications list only once per session
    if 'monthly_comparison_apps_list' not in st.session_state:
        with st.spinner("Loading applications..."):
            st.session_state.monthly_comparison_apps_list = get_all_application_names()

    all_apps_list = st.session_state.monthly_comparison_apps_list

    if not all_apps_list:
        st.warning("⚠️ No applications found in the database.")
        st.info("Please upload and process an Excel file first via the **Excel Upload** page.")

        if st.button("🔄 Reload Applications", key="reload_apps_list"):
            del st.session_state.monthly_comparison_apps_list
            st.rerun()
    else:
        # Display total available applications
        st.info(f"📊 {len(all_apps_list)} applications available for comparison")

        # Use a form to batch all inputs and prevent reruns on every selection
        with st.form(key="monthly_comparison_form"):
            st.markdown("### 📋 Configure Comparison")

            col_app_select, col_date_range = st.columns([2, 2])

            with col_app_select:
                st.markdown("**Select Applications (Max 5)**")
                selected_apps_comparison = st.multiselect(
                    "Choose 1 to 5 applications",
                    options=all_apps_list,
                    default=[],
                    max_selections=5,
                    help="Select up to 5 applications to compare their monthly costs",
                    label_visibility="collapsed"
                )

            with col_date_range:
                st.markdown("**Select Date Range**")
                col_start, col_end = st.columns(2)

                with col_start:
                    st.caption("From:")
                    start_year_comp = st.selectbox(
                        "Start Year",
                        options=list(range(2023, 2026)),
                        index=1,  # Default to 2024
                        label_visibility="collapsed"
                    )
                    start_month_comp = st.selectbox(
                        "Start Month",
                        options=list(range(1, 13)),
                        format_func=lambda x: [
                            "January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"
                        ][x-1],
                        index=0,  # Default to January
                        label_visibility="collapsed"
                    )

                with col_end:
                    st.caption("To:")
                    end_year_comp = st.selectbox(
                        "End Year",
                        options=list(range(2023, 2026)),
                        index=1,  # Default to 2024
                        label_visibility="collapsed"
                    )
                    end_month_comp = st.selectbox(
                        "End Month",
                        options=list(range(1, 13)),
                        format_func=lambda x: [
                            "January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"
                        ][x-1],
                        index=11,  # Default to December
                        label_visibility="collapsed"
                    )

            # Submit button inside the form
            submitted = st.form_submit_button(
                "📈 Analyze Monthly Trends",
                type="primary",
                use_container_width=True
            )

        # Add manual reload button outside the form
        if st.button("🔄 Reload Applications List", help="Refresh the applications list from database"):
            if 'monthly_comparison_apps_list' in st.session_state:
                del st.session_state.monthly_comparison_apps_list
            st.rerun()

        # Process form submission
        if submitted:
            if not selected_apps_comparison:
                st.warning("⚠️ Please select at least one application")
            else:
                # Build date range strings
                start_date_comp = f"{start_year_comp:04d}-{start_month_comp:02d}-01"
                end_date_comp = f"{end_year_comp:04d}-{end_month_comp:02d}-31"

                # Validate date range
                if start_date_comp > end_date_comp:
                    st.error("❌ Start date must be before end date")
                else:
                    # Show selected parameters
                    st.success(f"✅ Analyzing {len(selected_apps_comparison)} application(s) from {start_month_comp}/{start_year_comp} to {end_month_comp}/{end_year_comp}")

                    with st.spinner("Loading monthly cost data..."):
                        monthly_data = get_monthly_cost_by_applications(
                            selected_apps_comparison,
                            start_date_comp,
                            end_date_comp
                        )

                    if monthly_data:
                        # Convert to DataFrame for easier manipulation
                        df_monthly_comp = pd.DataFrame(monthly_data)

                        # Show summary metrics
                        st.markdown("---")
                        st.markdown("### 📊 Summary Metrics")

                        metric_cols = st.columns(len(selected_apps_comparison))

                        for idx, app in enumerate(selected_apps_comparison):
                            app_df = df_monthly_comp[df_monthly_comp["application"] == app]
                            total_cost = app_df["total_cost"].sum()
                            avg_monthly_cost = app_df["total_cost"].mean()
                            num_months = len(app_df)

                            with metric_cols[idx]:
                                st.metric(
                                    label=f"**{app}**",
                                    value=f"${total_cost:,.2f}",
                                    help=f"Total: ${total_cost:,.2f}\nAvg/month: ${avg_monthly_cost:,.2f}\nMonths: {num_months}"
                                )

                        st.markdown("---")
                        st.markdown("### 📈 Monthly Cost Trend")

                        # Create line chart with Plotly
                        fig = go.Figure()

                        for app in selected_apps_comparison:
                            app_df = df_monthly_comp[df_monthly_comp["application"] == app]
                            fig.add_trace(go.Scatter(
                                x=app_df["month"],
                                y=app_df["total_cost"],
                                mode='lines+markers',
                                name=app,
                                hovertemplate="<b>%{fullData.name}</b><br>Month: %{x}<br>Cost: $%{y:,.2f}<extra></extra>"
                            ))

                        fig.update_layout(
                            title=f"Monthly Cost Comparison ({start_month_comp}/{start_year_comp} - {end_month_comp}/{end_year_comp})",
                            xaxis_title="Month",
                            yaxis_title="Total Cost ($)",
                            hovermode='x unified',
                            height=500,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        # Show data table
                        st.markdown("---")
                        st.markdown("### 📋 Monthly Cost Data Table")

                        # Pivot the data for better readability
                        pivot_df = df_monthly_comp.pivot(
                            index="month",
                            columns="application",
                            values="total_cost"
                        ).fillna(0)

                        # Format the data
                        display_pivot = pivot_df.copy()
                        for col in display_pivot.columns:
                            display_pivot[col] = display_pivot[col].apply(lambda x: f"${x:,.2f}")

                        st.dataframe(display_pivot, use_container_width=True)

                        # Download option
                        st.markdown("---")
                        col_download1, col_download2 = st.columns([1, 3])

                        with col_download1:
                            csv = df_monthly_comp.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Monthly Cost Data (CSV)",
                                data=csv,
                                file_name=f"monthly_cost_comparison_{start_year_comp}{start_month_comp:02d}_{end_year_comp}{end_month_comp:02d}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )

                        with col_download2:
                            st.caption(f"💾 Download includes {len(df_monthly_comp)} records with application, month, total cost, and record count")

                    else:
                        st.warning("⚠️ No cost data found for the selected applications and date range")
                        st.info("Try selecting different applications or expanding the date range")


if __name__ == "__main__":
    main()
