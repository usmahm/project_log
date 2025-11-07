"""
Submit Log Page

This page allows students to submit their weekly project logs.
"""

import streamlit as st
from datetime import datetime
from utils.auth import require_login, get_current_user
from utils.database import create_log, check_existing_log
from utils.email_sender import send_verification_email

st.set_page_config(
    page_title="Submit Log",
    page_icon="📝",
    layout="wide"
)

# Require login to access this page
require_login()

st.title("📝 Submit Weekly Log")
st.markdown("---")

# Get current user
username = get_current_user()

# Calculate current week number (you can customize this logic)
current_week = datetime.now().isocalendar()[1]  # ISO week number

# Instructions
with st.expander("ℹ️ How to submit a log", expanded=False):
    st.markdown("""
    ### Guidelines for your weekly log:

    1. **Be specific**: Describe what you worked on this week
    2. **Mention achievements**: What did you complete or accomplish?
    3. **Note challenges**: Any problems you encountered?
    4. **Next steps**: What are you planning for next week?
    5. **Be honest**: Your supervisor is here to help you succeed

    **Example format:**
    ```
    Week 5 Progress Report

    This week I worked on:
    - Designed the database schema for the user authentication module
    - Implemented login and registration endpoints
    - Created unit tests for authentication functions

    Challenges:
    - Had trouble with password hashing initially, but resolved it using bcrypt

    Next week:
    - Integrate authentication with the frontend
    - Add session management
    ```
    """)

# Main form
col1, col2 = st.columns([2, 1])

with col1:
    with st.form("log_submission_form"):
        st.subheader("Enter Your Log Details")

        # Week number input
        week_number = st.number_input(
            "Week Number",
            min_value=1,
            max_value=52,
            value=current_week,
            help="Enter the week number for this log (1-52)"
        )

        # Check if log already exists for this week
        existing_log = check_existing_log(username, week_number)

        if existing_log:
            st.warning(f"""
            ⚠️ You have already submitted a log for Week {week_number}.

            **Status**: {existing_log['verified'].title()}
            **Submitted**: {existing_log['submitted_at'].strftime('%Y-%m-%d %H:%M')}

            You can view this log in the "View Logs" page.
            """)

        # Log content (large text area)
        log_content = st.text_area(
            "Log Content",
            height=300,
            placeholder="Enter your weekly project update here...\n\nDescribe what you worked on, what you accomplished, challenges you faced, and your plans for next week.",
            help="Write a detailed update about your project progress this week"
        )

        # Submit button
        submit_button = st.form_submit_button(
            "Submit Log",
            type="primary",
            use_container_width=True,
            disabled=existing_log is not None  # Disable if log already exists
        )

        if submit_button:
            # Validation
            if not log_content or len(log_content.strip()) < 50:
                st.error("Please enter a detailed log (at least 50 characters)")
            else:
                try:
                    # Create the log in database
                    log_id = create_log(username, week_number, log_content.strip())

                    # Get student and supervisor info from database
                    from utils.database import get_student_by_username

                    student = get_student_by_username(username)

                    # Send verification email to supervisor
                    success, message = send_verification_email(
                        log_id=log_id,
                        student_name=student['name'],
                        student_email=student['email'],
                        supervisor_email=student['supervisor_email'],
                        week_number=week_number,
                        log_content=log_content.strip()
                    )

                    if success:
                        st.success(f"""
                        ✅ Log submitted successfully!

                        **Week**: {week_number}
                        **Submitted**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

                        {message}

                        You can view this log in the "View Logs" page.
                        """)
                        st.balloons()  # Fun celebration animation!
                    else:
                        st.warning(f"""
                        ⚠️ Log saved, but email notification failed.

                        Your log has been saved to the database, but we couldn't send
                        the verification email to your supervisor.

                        Error: {message}

                        Please contact your administrator.
                        """)

                except Exception as e:
                    st.error(f"Failed to submit log: {str(e)}")

with col2:
    st.subheader("📊 Quick Stats")

    # Show student's submission history
    from utils.database import get_student_logs

    logs = get_student_logs(username)

    st.metric("Total Submissions", len(logs))

    if logs:
        approved = sum(1 for log in logs if log['verified'] == 'approved')
        pending = sum(1 for log in logs if log['verified'] == 'pending')
        rejected = sum(1 for log in logs if log['verified'] == 'rejected')

        st.metric("Approved", approved)
        st.metric("Pending", pending)
        if rejected > 0:
            st.metric("Rejected", rejected)

    st.markdown("---")

    # Tips section
    st.info("""
    💡 **Tips**

    - Submit logs regularly
    - Be detailed and specific
    - Include code snippets if relevant
    - Mention learning outcomes
    """)

    # Current week info
    st.markdown("---")
    st.caption(f"Current ISO Week: {current_week}")
    st.caption(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
