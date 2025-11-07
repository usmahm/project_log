"""
View Logs Page

This page displays all past log submissions with their verification status.
"""

import streamlit as st
import pandas as pd
from utils.auth import require_login, get_current_user
from utils.database import get_student_logs

st.set_page_config(
    page_title="View Logs",
    page_icon="📋",
    layout="wide"
)

# Require login
require_login()

st.title("📋 My Log History")
st.markdown("View all your submitted logs and their verification status")
st.markdown("---")

# Get current user and their logs
username = get_current_user()
logs = get_student_logs(username)

if not logs:
    st.info("You haven't submitted any logs yet. Head over to the Submit Log page to create your first entry!")
else:
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Submissions", len(logs))
    with col2:
        approved = sum(1 for log in logs if log['verified'] == 'approved')
        st.metric("Approved", approved, delta=None, delta_color="normal")
    with col3:
        pending = sum(1 for log in logs if log['verified'] == 'pending')
        st.metric("Pending", pending)
    with col4:
        rejected = sum(1 for log in logs if log['verified'] == 'rejected')
        st.metric("Rejected", rejected, delta=None, delta_color="inverse")

    st.markdown("---")

    # Filter options
    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "Pending", "Approved", "Rejected"],
            index=0
        )

    with col_filter2:
        sort_order = st.selectbox(
            "Sort by Week",
            options=["Newest First", "Oldest First"],
            index=0
        )

    # Apply filters
    filtered_logs = logs.copy()

    if status_filter != "All":
        filtered_logs = [log for log in filtered_logs if log['verified'] == status_filter.lower()]

    if sort_order == "Oldest First":
        filtered_logs = sorted(filtered_logs, key=lambda x: x['week_number'])
    else:
        filtered_logs = sorted(filtered_logs, key=lambda x: x['week_number'], reverse=True)

    st.markdown(f"**Showing {len(filtered_logs)} log(s)**")
    st.markdown("---")

    # Display logs as expandable cards
    for log in filtered_logs:
        # Status badge color
        if log['verified'] == 'approved':
            status_emoji = "✅"
            status_color = "green"
        elif log['verified'] == 'rejected':
            status_emoji = "❌"
            status_color = "red"
        else:
            status_emoji = "⏳"
            status_color = "orange"

        # Create expandable section for each log
        with st.expander(
            f"{status_emoji} Week {log['week_number']} - {log['submitted_at'].strftime('%Y-%m-%d')} - **{log['verified'].title()}**",
            expanded=False
        ):
            # Log details in columns
            detail_col1, detail_col2 = st.columns([3, 1])

            with detail_col1:
                st.markdown("#### Log Content")
                st.markdown(f"""
                <div style="background-color: #1e1e1e; color: #e0e0e0; padding: 15px; border-radius: 5px; white-space: pre-wrap; border-left: 4px solid {status_color};">
{log['content']}
                </div>
                """, unsafe_allow_html=True)

            with detail_col2:
                st.markdown("#### Details")
                st.write(f"**Week**: {log['week_number']}")
                st.write(f"**Submitted**: {log['submitted_at'].strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Status**: {status_emoji} {log['verified'].title()}")

                # Status-specific info
                if log['verified'] == 'pending':
                    st.info("Waiting for supervisor verification")
                elif log['verified'] == 'approved':
                    st.success("Approved by supervisor")
                elif log['verified'] == 'rejected':
                    st.error("Rejected - Please contact your supervisor")

    # Summary table (alternative view)
    st.markdown("---")
    st.subheader("📊 Summary Table")

    # Convert to DataFrame for table display
    df_data = []
    for log in logs:
        df_data.append({
            "Week": log['week_number'],
            "Submitted": log['submitted_at'].strftime('%Y-%m-%d'),
            "Status": log['verified'].title(),
            "Preview": log['content'][:100] + "..." if len(log['content']) > 100 else log['content']
        })

    df = pd.DataFrame(df_data)

    # Display as interactive table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Week": st.column_config.NumberColumn("Week #", format="%d"),
            "Submitted": st.column_config.TextColumn("Submission Date"),
            "Status": st.column_config.TextColumn("Status"),
            "Preview": st.column_config.TextColumn("Content Preview", width="large")
        }
    )

    # Export option
    st.markdown("---")
    if st.button("📥 Export All Logs as CSV"):
        export_data = []
        for log in logs:
            export_data.append({
                "Week Number": log['week_number'],
                "Submitted Date": log['submitted_at'].strftime('%Y-%m-%d %H:%M:%S'),
                "Status": log['verified'],
                "Content": log['content']
            })

        export_df = pd.DataFrame(export_data)
        csv = export_df.to_csv(index=False)

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"my_logs_{username}.csv",
            mime="text/csv"
        )
