"""
Drill Down Analysis - Hierarchical cost analysis by Application → Environment → Owner
"""
import streamlit as st
import pandas as pd
import os
import sys
import logging
import plotly.express as px
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
    page_title="Drill Down Analysis",
    page_icon="📊",
    layout="wide"
)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_date_range(months: int) -> tuple:
    """Calculate start and end dates for the last N months"""
    try:
        today = datetime.now()
        start_date = today - relativedelta(months=months)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = today.strftime("%Y-%m-%d")
        return start_str, end_str
    except Exception as e:
        logger.error(f"Error calculating date range: {e}")
        return None, None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cost_by_application(months: int) -> List[Dict]:
    """Get total cost grouped by application for the last N months"""
    try:
        collection = get_collection()
        start_date, end_date = get_date_range(months)

        if not start_date or not end_date:
            return []

        pipeline = [
            {"$match": {"date": {"$gte": start_date, "$lte": end_date}}},
            {"$project": {"applicationName": 1, "cost": 1}},
            {
                "$addFields": {
                    "numericCost": {
                        "$convert": {
                            "input": "$cost",
                            "to": "double",
                            "onError": 0,
                            "onNull": 0
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$applicationName",
                    "totalCost": {"$sum": "$numericCost"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"totalCost": -1}}
        ]

        results = list(collection.aggregate(pipeline, allowDiskUse=True))

        return [
            {
                "application": r["_id"],
                "total_cost": round(r["totalCost"], 2),
                "count": r["count"]
            }
            for r in results if r["_id"]
        ]
    except Exception as e:
        logger.error(f"Error getting cost by application: {e}")
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cost_by_environment(application: str, months: int) -> List[Dict]:
    """Get total cost grouped by environment for a specific application"""
    try:
        collection = get_collection()
        start_date, end_date = get_date_range(months)

        if not start_date or not end_date:
            return []

        pipeline = [
            {
                "$match": {
                    "applicationName": application,
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {"$project": {"environment": 1, "cost": 1}},
            {
                "$addFields": {
                    "numericCost": {
                        "$convert": {
                            "input": "$cost",
                            "to": "double",
                            "onError": 0,
                            "onNull": 0
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$environment",
                    "totalCost": {"$sum": "$numericCost"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"totalCost": -1}}
        ]

        results = list(collection.aggregate(pipeline, allowDiskUse=True))

        return [
            {
                "environment": r["_id"],
                "total_cost": round(r["totalCost"], 2),
                "count": r["count"]
            }
            for r in results if r["_id"]
        ]
    except Exception as e:
        logger.error(f"Error getting cost by environment: {e}")
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cost_by_owner(application: str, environment: str, months: int) -> List[Dict]:
    """Get total cost grouped by owner for a specific application and environment"""
    try:
        collection = get_collection()
        start_date, end_date = get_date_range(months)

        if not start_date or not end_date:
            return []

        pipeline = [
            {
                "$match": {
                    "applicationName": application,
                    "environment": environment,
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {"$project": {"owner": 1, "cost": 1}},
            {
                "$addFields": {
                    "numericCost": {
                        "$convert": {
                            "input": "$cost",
                            "to": "double",
                            "onError": 0,
                            "onNull": 0
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$owner",
                    "totalCost": {"$sum": "$numericCost"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"totalCost": -1}}
        ]

        results = list(collection.aggregate(pipeline, allowDiskUse=True))

        return [
            {
                "owner": r["_id"],
                "total_cost": round(r["totalCost"], 2),
                "count": r["count"]
            }
            for r in results if r["_id"]
        ]
    except Exception as e:
        logger.error(f"Error getting cost by owner: {e}")
        return []


def main():
    """Main drill down analysis page"""

    st.title("📊 Drill Down Analysis")
    st.markdown("Interactive hierarchical drill-down analysis of costs by Application → Environment → Owner.")

    # Add reload button in the top right
    col_title, col_reload_btn = st.columns([4, 1])
    with col_reload_btn:
        if st.button("🔄 Reset Analysis", help="Clear cache and restart analysis", use_container_width=True):
            # Clear cache
            get_date_range.clear()
            get_cost_by_application.clear()
            get_cost_by_environment.clear()
            get_cost_by_owner.clear()
            # Reset state
            st.session_state.drill_down_level = 1
            st.session_state.selected_application = None
            st.session_state.selected_environment = None
            st.session_state.drill_down_data_loaded = False
            st.rerun()

    # Test MongoDB connection
    if not test_connection():
        st.error("❌ Cannot connect to MongoDB. Please check if MongoDB is running on localhost:27017")
        st.info("To start MongoDB, run: `mongod` or `brew services start mongodb-community`")
        return

    # Initialize drill-down state
    if 'drill_down_level' not in st.session_state:
        st.session_state.drill_down_level = 1  # Level 1: Application
        st.session_state.selected_application = None
        st.session_state.selected_environment = None
        st.session_state.drill_down_data_loaded = False  # Track if data is loaded

    # Filters row
    col_filter1, col_filter2, col_filter3 = st.columns([1, 1, 2])

    with col_filter1:
        time_period_map = {
            "Last 3 Months": 3,
            "Last 6 Months": 6,
            "Last 9 Months": 9,
            "Last 1 Year": 12
        }

        selected_period = st.selectbox(
            "Time Period",
            options=list(time_period_map.keys()),
            key="detailed_analysis_period",
            on_change=lambda: setattr(st.session_state, 'drill_down_data_loaded', False)
        )

        months = time_period_map[selected_period]

    with col_filter2:
        # Top N filter - only show at Level 1
        if st.session_state.drill_down_level == 1:
            top_n_options = ["All", "Top 5", "Top 10"]
            top_n_filter = st.selectbox(
                "Show Applications",
                options=top_n_options,
                key="top_n_filter",
                help="Filter applications by highest cost",
                on_change=lambda: setattr(st.session_state, 'drill_down_data_loaded', False)
            )
        else:
            top_n_filter = "All"

    with col_filter3:
        # Breadcrumb navigation
        if st.session_state.drill_down_level == 1:
            filter_text = f" - {top_n_filter}" if top_n_filter != "All" else ""
            st.info(f"📊 **Current View:** Applications ({selected_period}){filter_text}")
        elif st.session_state.drill_down_level == 2:
            breadcrumb = f"📊 **Navigation:** All Applications > **{st.session_state.selected_application}**"
            st.info(breadcrumb)
            if st.button("⬅️ Back to Applications", key="back_to_apps"):
                st.session_state.drill_down_level = 1
                st.session_state.selected_application = None
                st.session_state.drill_down_data_loaded = True  # Keep data loaded when going back
                st.rerun()
        elif st.session_state.drill_down_level == 3:
            breadcrumb = f"📊 **Navigation:** All Applications > {st.session_state.selected_application} > **{st.session_state.selected_environment}**"
            st.info(breadcrumb)
            col_back1, col_back2 = st.columns(2)
            with col_back1:
                if st.button("⬅️ Back to Environments", key="back_to_envs"):
                    st.session_state.drill_down_level = 2
                    st.session_state.selected_environment = None
                    st.rerun()
            with col_back2:
                if st.button("⬅️⬅️ Back to Applications", key="back_to_apps_from_owner"):
                    st.session_state.drill_down_level = 1
                    st.session_state.selected_application = None
                    st.session_state.selected_environment = None
                    st.session_state.drill_down_data_loaded = True  # Keep data loaded when going back
                    st.rerun()

    st.markdown("---")

    # Level 1: Cost by Application
    if st.session_state.drill_down_level == 1:
        st.markdown("### 💼 Cost by Application Name")

        # Show "Start Analysis" button if data not loaded yet
        if not st.session_state.drill_down_data_loaded:
            st.info("👆 Configure your analysis settings above, then click the button below to load the data.")

            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("🚀 Start Analysis", type="primary", use_container_width=True, key="start_drill_down"):
                    st.session_state.drill_down_data_loaded = True
                    st.rerun()

            st.info("💡 **Tip:** This page loads data only when you're ready, making it lightning-fast!")
            return  # Don't load data yet

        st.caption("💡 Click on any bar in the chart to drill down into environments for that application")

        with st.spinner(f"Loading application costs for {selected_period.lower()}..."):
            app_data = get_cost_by_application(months)

        if app_data:
            # Store total count before filtering
            total_app_count = len(app_data)

            # Apply Top N filter
            if top_n_filter == "Top 5":
                app_data = app_data[:5]
                st.info(f"📊 Showing top 5 applications by highest cost out of {total_app_count} total")
            elif top_n_filter == "Top 10":
                app_data = app_data[:10]
                st.info(f"📊 Showing top 10 applications by highest cost out of {total_app_count} total")

            df_apps = pd.DataFrame(app_data)

            # Create interactive bar chart
            fig = px.bar(
                df_apps,
                x="application",
                y="total_cost",
                title=f"Total Cost by Application ({selected_period})",
                labels={"application": "Application Name", "total_cost": "Total Cost ($)"},
                color="total_cost",
                color_continuous_scale="Viridis",
                hover_data={"count": True, "total_cost": ":,.2f"}
            )

            fig.update_layout(
                xaxis_tickangle=-45,
                showlegend=False,
                height=500,
                xaxis_title="Application Name",
                yaxis_title="Total Cost ($)"
            )

            fig.update_traces(
                hovertemplate="<b>%{x}</b><br>Cost: $%{y:,.2f}<br>Records: %{customdata[0]}<extra></extra>"
            )

            # Display chart with click event handling
            event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="app_chart")

            # Data table
            st.markdown("**Application Cost Details:**")

            display_df = df_apps.copy()
            display_df.columns = ["Application", "Total Cost ($)", "Record Count"]
            display_df["Total Cost ($)"] = display_df["Total Cost ($)"].apply(lambda x: f"${x:,.2f}")
            display_df["Record Count"] = display_df["Record Count"].apply(lambda x: f"{x:,}")

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Handle chart click event
            if event and "selection" in event and "points" in event["selection"]:
                points = event["selection"]["points"]
                if points and len(points) > 0:
                    # Get the clicked application name from the x-axis value
                    clicked_app = points[0].get("x")
                    if clicked_app:
                        st.session_state.selected_application = clicked_app
                        st.session_state.drill_down_level = 2
                        st.rerun()

        else:
            st.warning(f"No data available for {selected_period.lower()}")

    # Level 2: Cost by Environment
    elif st.session_state.drill_down_level == 2:
        st.markdown(f"### 🌍 Cost by Environment for **{st.session_state.selected_application}**")
        st.caption("💡 Click on any bar in the chart to drill down into owners for that environment")

        with st.spinner(f"Loading environment costs for {st.session_state.selected_application}..."):
            env_data = get_cost_by_environment(st.session_state.selected_application, months)

        if env_data:
            df_envs = pd.DataFrame(env_data)

            # Create interactive bar chart
            fig = px.bar(
                df_envs,
                x="environment",
                y="total_cost",
                title=f"Cost by Environment - {st.session_state.selected_application} ({selected_period})",
                labels={"environment": "Environment", "total_cost": "Total Cost ($)"},
                color="total_cost",
                color_continuous_scale="Plasma",
                hover_data={"count": True, "total_cost": ":,.2f"}
            )

            fig.update_layout(
                xaxis_tickangle=-45,
                showlegend=False,
                height=500,
                xaxis_title="Environment",
                yaxis_title="Total Cost ($)"
            )

            fig.update_traces(
                hovertemplate="<b>%{x}</b><br>Cost: $%{y:,.2f}<br>Records: %{customdata[0]}<extra></extra>"
            )

            # Display chart with click event handling
            event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="env_chart")

            # Data table
            st.markdown("**Environment Cost Details:**")

            display_df = df_envs.copy()
            display_df.columns = ["Environment", "Total Cost ($)", "Record Count"]
            display_df["Total Cost ($)"] = display_df["Total Cost ($)"].apply(lambda x: f"${x:,.2f}")
            display_df["Record Count"] = display_df["Record Count"].apply(lambda x: f"{x:,}")

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Handle chart click event
            if event and "selection" in event and "points" in event["selection"]:
                points = event["selection"]["points"]
                if points and len(points) > 0:
                    # Get the clicked environment name from the x-axis value
                    clicked_env = points[0].get("x")
                    if clicked_env:
                        st.session_state.selected_environment = clicked_env
                        st.session_state.drill_down_level = 3
                        st.rerun()

        else:
            st.warning(f"No environment data available for {st.session_state.selected_application}")

    # Level 3: Cost by Owner
    elif st.session_state.drill_down_level == 3:
        st.markdown(f"### 👤 Cost by Owner")
        st.markdown(f"**Application:** {st.session_state.selected_application} | **Environment:** {st.session_state.selected_environment}")

        with st.spinner("Loading owner costs..."):
            owner_data = get_cost_by_owner(
                st.session_state.selected_application,
                st.session_state.selected_environment,
                months
            )

        if owner_data:
            df_owners = pd.DataFrame(owner_data)

            # Create interactive bar chart
            fig = px.bar(
                df_owners,
                x="owner",
                y="total_cost",
                title=f"Cost by Owner - {st.session_state.selected_application} / {st.session_state.selected_environment} ({selected_period})",
                labels={"owner": "Owner", "total_cost": "Total Cost ($)"},
                color="total_cost",
                color_continuous_scale="Cividis",
                hover_data={"count": True, "total_cost": ":,.2f"}
            )

            fig.update_layout(
                xaxis_tickangle=-45,
                showlegend=False,
                height=500,
                xaxis_title="Owner",
                yaxis_title="Total Cost ($)"
            )

            fig.update_traces(
                hovertemplate="<b>%{x}</b><br>Cost: $%{y:,.2f}<br>Records: %{customdata[0]}<extra></extra>"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Data table
            st.markdown("**Owner Cost Details:**")

            display_df = df_owners.copy()
            display_df.columns = ["Owner", "Total Cost ($)", "Record Count"]
            display_df["Total Cost ($)"] = display_df["Total Cost ($)"].apply(lambda x: f"${x:,.2f}")
            display_df["Record Count"] = display_df["Record Count"].apply(lambda x: f"{x:,}")

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Download option
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Owner Cost Data",
                data=csv,
                file_name=f"owner_costs_{st.session_state.selected_application}_{st.session_state.selected_environment}.csv",
                mime="text/csv"
            )

        else:
            st.warning(f"No owner data available for {st.session_state.selected_application} / {st.session_state.selected_environment}")


if __name__ == "__main__":
    main()
