"""
Cost Analysis Page - Analyze costs based on Application, Environment, Owner, and Date range
"""
import streamlit as st
import pandas as pd
import os
import sys
import logging
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
import time
import json

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
    page_title="Cost Analysis",
    page_icon="💰",
    layout="wide"
)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_unique_values(field: str) -> List[str]:
    """Get unique values for a specific field (cached)"""
    try:
        collection = get_collection()
        # Use aggregation with limit to make it faster for large datasets
        pipeline = [
            {"$group": {"_id": f"${field}"}},
            {"$match": {"_id": {"$ne": None, "$ne": ""}}},
            {"$sort": {"_id": 1}},
            {"$limit": 1000}  # Limit to 1000 unique values for performance
        ]
        results = list(collection.aggregate(pipeline))
        unique_values = [str(r["_id"]) for r in results]
        return unique_values
    except Exception as e:
        logger.error(f"Error getting unique values for {field}: {e}")
        return []


def calculate_cost_by_entity(filters: Dict, group_by_fields: List[str], include_monthly: bool = False) -> List[Dict]:
    """
    Calculate costs grouped by specified fields (e.g., applicationName, environment, owner).
    Each entity (combination of group_by fields) is treated separately.
    """
    try:
        collection = get_collection()

        # Build the base pipeline
        pipeline = []

        # Add match stage if filters exist
        if filters:
            pipeline.append({"$match": filters})

        # Project needed fields
        project_fields = {"cost": 1, "applicationName": 1, "environment": 1, "owner": 1}
        if include_monthly:
            project_fields["date"] = 1

        pipeline.append({"$project": project_fields})

        # Add cost conversion
        pipeline.append({
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
        })

        if include_monthly:
            # Add month extraction
            pipeline.append({
                "$addFields": {
                    "yearMonth": {"$substr": ["$date", 0, 7]}
                }
            })

            # Group by entities AND month
            group_id = {}
            for field in group_by_fields:
                group_id[field] = f"${field}"
            group_id["month"] = "$yearMonth"

            pipeline.append({
                "$group": {
                    "_id": group_id,
                    "totalCost": {"$sum": "$numericCost"},
                    "count": {"$sum": 1},
                    "avgCost": {"$avg": "$numericCost"},
                    "minCost": {"$min": "$numericCost"},
                    "maxCost": {"$max": "$numericCost"}
                }
            })
            pipeline.append({"$sort": {"_id.month": 1}})
        else:
            # Group by entities only
            group_id = {}
            for field in group_by_fields:
                group_id[field] = f"${field}"

            pipeline.append({
                "$group": {
                    "_id": group_id,
                    "totalCost": {"$sum": "$numericCost"},
                    "count": {"$sum": 1},
                    "avgCost": {"$avg": "$numericCost"},
                    "minCost": {"$min": "$numericCost"},
                    "maxCost": {"$max": "$numericCost"}
                }
            })
            pipeline.append({"$sort": {"totalCost": -1}})

        # Execute aggregation
        results = list(collection.aggregate(pipeline, allowDiskUse=True))

        # Format results
        formatted_results = []
        for r in results:
            entity = {}
            for field in group_by_fields:
                entity[field] = r["_id"].get(field, "N/A")

            result_item = {
                **entity,
                "total_cost": round(r["totalCost"], 2),
                "count": r["count"],
                "avg_cost": round(r["avgCost"], 2),
                "min_cost": round(r["minCost"], 2),
                "max_cost": round(r["maxCost"], 2)
            }

            if include_monthly:
                result_item["month"] = r["_id"].get("month", "")

            formatted_results.append(result_item)

        return formatted_results

    except Exception as e:
        logger.error(f"Error calculating cost by entity: {e}")
        return []


def main():
    """Main cost analysis page function"""

    st.title("💰 Cost Analysis")
    st.markdown("Analyze costs based on Application, Environment, Owner, and Date range.")

    # Test MongoDB connection
    if not test_connection():
        st.error("❌ Cannot connect to MongoDB. Please check if MongoDB is running on localhost:27017")
        st.info("To start MongoDB, run: `mongod` or `brew services start mongodb-community`")
        return

    st.markdown("---")

    # Lazy load unique values only when page is accessed - use session state for caching
    if 'cost_analysis_loaded' not in st.session_state:
        with st.spinner("Loading filter options..."):
            st.session_state.unique_apps = get_unique_values("applicationName")
            st.session_state.unique_envs = get_unique_values("environment")
            st.session_state.unique_owners = get_unique_values("owner")
            st.session_state.cost_analysis_loaded = True

    unique_apps = st.session_state.unique_apps
    unique_envs = st.session_state.unique_envs
    unique_owners = st.session_state.unique_owners

    # Add refresh and clear buttons for filters
    col_header1, col_header2, col_header3 = st.columns([3, 1, 1])
    with col_header1:
        st.markdown("### 📋 Select Filters")
    with col_header2:
        if st.button("🗑️ Clear", help="Clear all filter selections", use_container_width=True):
            # Clear multiselect values by removing from session state
            if 'cost_apps' in st.session_state:
                del st.session_state.cost_apps
            if 'cost_envs' in st.session_state:
                del st.session_state.cost_envs
            if 'cost_owners' in st.session_state:
                del st.session_state.cost_owners
            st.rerun()
    with col_header3:
        if st.button("🔄 Refresh", help="Reload filter options from database", use_container_width=True):
            st.session_state.cost_analysis_loaded = False
            st.cache_data.clear()
            st.rerun()

    col1, col2, col3 = st.columns(3)

    with col1:
        # Application Name with multi-select
        selected_apps = st.multiselect(
            "Application Name",
            options=unique_apps,
            default=[],
            key="cost_apps",
            help="Select one or more applications (leave empty for all)"
        )

    with col2:
        # Environment with multi-select
        selected_envs = st.multiselect(
            "Environment",
            options=unique_envs,
            default=[],
            key="cost_envs",
            help="Select one or more environments (leave empty for all)"
        )

    with col3:
        # Owner with multi-select
        selected_owners = st.multiselect(
            "Owner",
            options=unique_owners,
            default=[],
            key="cost_owners",
            help="Select one or more owners (leave empty for all)"
        )

    # Show selection summary
    total_selections = len(selected_apps) + len(selected_envs) + len(selected_owners)
    if total_selections > 0:
        summary_parts = []
        if selected_apps:
            summary_parts.append(f"**{len(selected_apps)}** app(s)")
        if selected_envs:
            summary_parts.append(f"**{len(selected_envs)}** env(s)")
        if selected_owners:
            summary_parts.append(f"**{len(selected_owners)}** owner(s)")

        st.info(f"🔍 Selected: {' + '.join(summary_parts)}")

    st.markdown("---")
    st.markdown("### 📅 Select Date Range")

    # Date range selection
    date_range_type = st.radio(
        "Date Range Type",
        options=["Single Month", "Month Range"],
        horizontal=True,
        key="date_range_type_selector",
        index=1  # Default to "Month Range" (index 1)
    )

    if date_range_type == "Single Month":
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            selected_year = st.selectbox(
                "Year",
                options=list(range(2023, 2026)),
                index=1,  # Default to 2024
                key="cost_single_year"
            )
        with col_date2:
            selected_month = st.selectbox(
                "Month",
                options=list(range(1, 13)),
                format_func=lambda x: [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ][x-1],
                key="cost_single_month"
            )
    else:  # Month Range
        col_start, col_end = st.columns(2)

        with col_start:
            st.markdown("**Start Date**")
            start_year = st.selectbox(
                "Start Year",
                options=list(range(2023, 2026)),
                index=1,  # Default to 2024
                key="cost_start_year"
            )
            start_month = st.selectbox(
                "Start Month",
                options=list(range(1, 13)),
                format_func=lambda x: [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ][x-1],
                index=10,  # Default to November (index 10 = month 11)
                key="cost_start_month"
            )

        with col_end:
            st.markdown("**End Date**")
            end_year = st.selectbox(
                "End Year",
                options=list(range(2023, 2026)),
                index=2,  # Default to 2025
                key="cost_end_year"
            )
            end_month = st.selectbox(
                "End Month",
                options=list(range(1, 13)),
                format_func=lambda x: [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ][x-1],
                index=9,  # Default to October (index 9 = month 10)
                key="cost_end_month"
            )

    st.markdown("---")

    # Calculate button
    if st.button("💵 Calculate Cost Analysis", type="primary", use_container_width=True):
        # Build filters
        filters = {}

        # Handle multi-select filters using $in operator
        if selected_apps and len(selected_apps) > 0:
            if len(selected_apps) == 1:
                filters["applicationName"] = selected_apps[0]
            else:
                filters["applicationName"] = {"$in": selected_apps}

        if selected_envs and len(selected_envs) > 0:
            if len(selected_envs) == 1:
                filters["environment"] = selected_envs[0]
            else:
                filters["environment"] = {"$in": selected_envs}

        if selected_owners and len(selected_owners) > 0:
            if len(selected_owners) == 1:
                filters["owner"] = selected_owners[0]
            else:
                filters["owner"] = {"$in": selected_owners}

        # Add date filter
        if date_range_type == "Single Month":
            # Create date pattern for single month (e.g., "2024-01" for January 2024)
            date_pattern = f"{selected_year:04d}-{selected_month:02d}"
            filters["date"] = {"$regex": f"^{date_pattern}"}
        else:
            # Create date range filter
            start_date = f"{start_year:04d}-{start_month:02d}"
            end_date = f"{end_year:04d}-{end_month:02d}"
            filters["date"] = {"$gte": start_date, "$lte": end_date + "-31"}

        # Determine grouping fields based on selections
        group_by_fields = []
        if selected_apps and len(selected_apps) > 0:
            group_by_fields.append("applicationName")
        if selected_envs and len(selected_envs) > 0:
            group_by_fields.append("environment")
        if selected_owners and len(selected_owners) > 0:
            group_by_fields.append("owner")

        # If no specific filters, default to grouping by applicationName
        if not group_by_fields:
            group_by_fields = ["applicationName"]

        # Create placeholder for spinner and timer
        spinner_placeholder = st.empty()
        timer_placeholder = st.empty()

        # Start timing
        start_time = time.time()

        with spinner_placeholder:
            with st.spinner("Calculating costs..."):
                # Calculate cost by entity (each app/env/owner separately)
                include_monthly_breakdown = (date_range_type == "Month Range")
                cost_results = calculate_cost_by_entity(filters, group_by_fields, include_monthly=include_monthly_breakdown)

        # End timing
        end_time = time.time()
        execution_time = end_time - start_time

        # Clear spinner and show execution time
        spinner_placeholder.empty()
        timer_placeholder.empty()

        if cost_results and len(cost_results) > 0:
            # Show success message with execution time
            st.success(f"✅ Cost analysis completed in **{execution_time:.2f} seconds**!")

            # Calculate totals across all entities
            if not include_monthly_breakdown:
                total_records = sum(r["count"] for r in cost_results)
                total_cost_all = sum(r["total_cost"] for r in cost_results)

                # Display query details in collapsible section
                with st.expander("📋 Query Details", expanded=False):
                    col_query1, col_query2 = st.columns(2)

                    with col_query1:
                        st.markdown("**Records Analyzed:**")
                        st.info(f"**{total_records:,}** records matched the query filters")

                    with col_query2:
                        st.markdown("**Execution Time:**")
                        st.info(f"Query completed in **{execution_time:.3f}** seconds")

                    st.markdown("**MongoDB Query (Match Stage):**")
                    st.code(json.dumps(filters, indent=2), language="json")

                    st.caption("💡 This is the filter used in the MongoDB aggregation pipeline's $match stage")

                # Show overall totals
                st.markdown("### 📊 Overall Summary")
                col_total1, col_total2 = st.columns(2)
                with col_total1:
                    st.metric("Total Cost (All Entities)", f"${total_cost_all:,.2f}")
                with col_total2:
                    st.metric("Total Records", f"{total_records:,}")

                st.markdown("---")

            # Display results for each entity
            st.markdown(f"### 💰 Cost Breakdown by {', '.join([f.replace('Name', '') for f in group_by_fields])}")

            # Create DataFrame for entity results (non-monthly view)
            if not include_monthly_breakdown:
                df_entities = pd.DataFrame(cost_results)

                # Display as a table with metrics
                for idx, entity in enumerate(cost_results):
                    # Build entity label
                    entity_labels = []
                    for field in group_by_fields:
                        if field in entity:
                            entity_labels.append(f"{field.replace('Name', '')}: **{entity[field]}**")

                    st.markdown(f"**{' | '.join(entity_labels)}**")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "Total Cost",
                            f"${entity['total_cost']:,.2f}",
                            help="Sum of all costs for this entity"
                        )

                    with col2:
                        st.metric(
                            "Records",
                            f"{entity['count']:,}",
                            help="Number of records for this entity"
                        )

                    with col3:
                        st.metric(
                            "Average Cost",
                            f"${entity['avg_cost']:,.2f}",
                            help="Average cost per record"
                        )

                    with col4:
                        st.metric(
                            "Cost Range",
                            f"${entity['min_cost']:,.2f} - ${entity['max_cost']:,.2f}",
                            help="Min and max cost values"
                        )

                    if idx < len(cost_results) - 1:
                        st.markdown("---")

                # Add comparison chart
                st.markdown("---")
                st.markdown("### 📊 Comparison Chart")

                col_chart1, col_chart2 = st.columns(2)

                with col_chart1:
                    # Bar chart comparing entities
                    # Create entity labels for chart
                    df_chart = df_entities.copy()
                    df_chart["entity_label"] = df_chart.apply(
                        lambda row: " | ".join([str(row[field]) for field in group_by_fields if field in row]),
                        axis=1
                    )

                    fig_bar = px.bar(
                        df_chart,
                        x="entity_label",
                        y="total_cost",
                        title="Cost Comparison by Entity",
                        labels={"entity_label": "Entity", "total_cost": "Total Cost ($)"},
                        color="total_cost",
                        color_continuous_scale="Blues",
                        text="total_cost"  # Show values on bars
                    )
                    fig_bar.update_layout(
                        xaxis_tickangle=-45,
                        showlegend=False,
                        height=400
                    )
                    fig_bar.update_traces(
                        texttemplate='$%{text:,.0f}',  # Format as currency
                        textposition='outside',  # Position text above bars
                        hovertemplate="<b>%{x}</b><br>Cost: $%{y:,.2f}<extra></extra>"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                with col_chart2:
                    # Pie chart showing cost distribution
                    fig_pie = px.pie(
                        df_chart,
                        values="total_cost",
                        names="entity_label",
                        title="Cost Distribution",
                        hole=0.4
                    )
                    fig_pie.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate="<b>%{label}</b><br>Cost: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>"
                    )
                    fig_pie.update_layout(height=400)
                    st.plotly_chart(fig_pie, use_container_width=True)

            # Show applied filters
            st.markdown("---")
            st.markdown("**Applied Filters:**")
            filter_summary = []

            # Show selected applications
            if selected_apps and len(selected_apps) > 0:
                if len(selected_apps) <= 3:
                    apps_display = ", ".join(selected_apps)
                else:
                    apps_display = f"{', '.join(selected_apps[:3])} and {len(selected_apps) - 3} more"
                filter_summary.append(f"**Application:** {apps_display}")

            # Show selected environments
            if selected_envs and len(selected_envs) > 0:
                if len(selected_envs) <= 3:
                    envs_display = ", ".join(selected_envs)
                else:
                    envs_display = f"{', '.join(selected_envs[:3])} and {len(selected_envs) - 3} more"
                filter_summary.append(f"**Environment:** {envs_display}")

            # Show selected owners
            if selected_owners and len(selected_owners) > 0:
                if len(selected_owners) <= 3:
                    owners_display = ", ".join(selected_owners)
                else:
                    owners_display = f"{', '.join(selected_owners[:3])} and {len(selected_owners) - 3} more"
                filter_summary.append(f"**Owner:** {owners_display}")

            if date_range_type == "Single Month":
                month_name = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ][selected_month-1]
                filter_summary.append(f"**Date:** {month_name} {selected_year}")
            else:
                start_month_name = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ][start_month-1]
                end_month_name = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ][end_month-1]
                filter_summary.append(f"**Date Range:** {start_month_name} {start_year} - {end_month_name} {end_year}")

            if filter_summary:
                for item in filter_summary:
                    st.markdown(f"- {item}")
            else:
                st.info("No specific filters applied - showing all data")

            # Add visualization for monthly breakdown
            if date_range_type == "Month Range" and include_monthly_breakdown:
                st.markdown("---")
                st.markdown("### 📊 Monthly Cost Trend by Entity")

                if cost_results and len(cost_results) > 0:
                    # Create DataFrame from monthly results
                    df_monthly = pd.DataFrame(cost_results)

                    # Create entity label
                    df_monthly["entity_label"] = df_monthly.apply(
                        lambda row: " | ".join([str(row[field]) for field in group_by_fields if field in row]),
                        axis=1
                    )

                    # Create visualizations
                    col_viz1, col_viz2 = st.columns(2)

                    with col_viz1:
                        # Line chart - Cost over time for each entity
                        fig = go.Figure()

                        # Group by entity and add trace for each
                        for entity_label in df_monthly["entity_label"].unique():
                            entity_data = df_monthly[df_monthly["entity_label"] == entity_label].sort_values("month")
                            fig.add_trace(go.Scatter(
                                x=entity_data["month"],
                                y=entity_data["total_cost"],
                                mode='lines+markers',
                                name=entity_label,
                                hovertemplate="<b>%{fullData.name}</b><br>Month: %{x}<br>Cost: $%{y:,.2f}<extra></extra>"
                            ))

                        fig.update_layout(
                            title="Monthly Cost Trend by Entity",
                            xaxis_title="Month",
                            yaxis_title="Total Cost ($)",
                            hovermode='x unified',
                            height=400,
                            legend=dict(
                                orientation="v",
                                yanchor="top",
                                y=1,
                                xanchor="left",
                                x=1.02
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with col_viz2:
                        # Stacked bar chart showing entity breakdown per month with totals
                        fig_stacked = px.bar(
                            df_monthly,
                            x="month",
                            y="total_cost",
                            color="entity_label",
                            title="Monthly Cost by Entity (Stacked)",
                            labels={"month": "Month", "total_cost": "Total Cost ($)", "entity_label": "Entity"},
                            barmode="stack",
                            text="total_cost"  # Show values on bars
                        )
                        fig_stacked.update_layout(
                            xaxis_tickangle=-45,
                            height=400,
                            legend=dict(
                                orientation="v",
                                yanchor="top",
                                y=1,
                                xanchor="left",
                                x=1.02
                            )
                        )
                        fig_stacked.update_traces(
                            texttemplate='$%{text:,.0f}',  # Format as currency with no decimals
                            textposition='inside',  # Position text inside bars
                            textfont=dict(color='white', size=11),  # White text for readability
                            hovertemplate="<b>%{fullData.name}</b><br>Month: %{x}<br>Cost: $%{y:,.2f}<extra></extra>"
                        )

                        # Add total per month on top of stacked bars
                        # Calculate total per month
                        monthly_totals = df_monthly.groupby("month")["total_cost"].sum().reset_index()

                        # Add invisible bar trace for totals on top
                        fig_stacked.add_trace(go.Bar(
                            x=monthly_totals["month"],
                            y=[0] * len(monthly_totals),  # Invisible bars
                            text=monthly_totals["total_cost"].apply(lambda x: f'${x:,.0f}'),
                            textposition='outside',
                            textfont=dict(size=13, color='white', family='Arial Black'),  # White text, larger size
                            showlegend=False,
                            hoverinfo='skip',
                            marker=dict(color='rgba(0,0,0,0)')  # Transparent
                        ))

                        st.plotly_chart(fig_stacked, use_container_width=True)

                    # Show data table with pivot
                    st.markdown("---")
                    st.markdown("**Monthly Cost Data Table:**")

                    # Pivot table: months as rows, entities as columns
                    pivot_df = df_monthly.pivot_table(
                        index="month",
                        columns="entity_label",
                        values="total_cost",
                        aggfunc="sum",
                        fill_value=0
                    )

                    # Format costs
                    display_pivot = pivot_df.copy()
                    for col in display_pivot.columns:
                        display_pivot[col] = display_pivot[col].apply(lambda x: f"${x:,.2f}")

                    st.dataframe(display_pivot, use_container_width=True)

                    # Download option
                    csv = df_monthly.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Monthly Cost Data (CSV)",
                        data=csv,
                        file_name=f"cost_analysis_monthly_{start_year}{start_month:02d}_{end_year}{end_month:02d}.csv",
                        mime="text/csv"
                    )

                else:
                    st.info("No monthly breakdown available for the selected date range")

        else:
            st.warning("⚠️ No data found matching the selected filters")


if __name__ == "__main__":
    main()
