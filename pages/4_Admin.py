"""
Admin Page

This page allows administrators to upload student data via CSV.
Requires admin authentication and filters students by department.
"""

import streamlit as st
import pandas as pd
from utils.auth import hash_password, require_admin_login, get_admin_department, get_admin_role, logout_admin
from utils.database import create_student, get_or_create_supervisor, get_all_students

st.set_page_config(
    page_title="Admin Panel",
    page_icon="👨‍💼",
    layout="wide"
)

# Require admin login
require_admin_login()

# Get admin info
admin_dept = get_admin_department()
admin_role = get_admin_role()
is_super_admin = (admin_role == "super_admin")

# Header with admin info
col_header1, col_header2 = st.columns([3, 1])

with col_header1:
    st.title("👨‍💼 Admin Panel")
    if is_super_admin:
        st.markdown("Upload student data and manage the system (All Departments)")
    else:
        st.markdown(f"Upload student data and manage the system (Department: **{admin_dept}**)")

with col_header2:
    if st.button("🔓 Logout", key="admin_logout"):
        logout_admin()
        st.success("Logged out successfully!")
        st.rerun()

st.markdown("---")

# Tabs for different admin functions
tab1, tab2, tab3 = st.tabs(["📤 Upload Students", "👥 View All Students", "📧 Test Email"])

# TAB 1: Upload Students
with tab1:
    st.subheader("Upload Student Data from CSV")

    # Instructions and CSV template
    with st.expander("📋 CSV Format Instructions", expanded=True):
        st.markdown("""
        ### Required CSV Format

        Your CSV file must have the following columns (in any order):

        - **username**: Student's unique identifier (e.g., student ID)
        - **name**: Student's full name
        - **email**: Student's email address
        - **supervisor_name**: Supervisor's full name
        - **supervisor_email**: Supervisor's email address
        - **password**: Temporary password for the student

        ### Example CSV:
        ```
        username,name,email,supervisor_name,supervisor_email,password
        S12345,John Doe,john.doe@university.edu,Dr. Smith,dr.smith@university.edu,TempPass123
        S12346,Jane Smith,jane.smith@university.edu,Dr. Jones,dr.jones@university.edu,TempPass456
        ```

        ### Important Notes:
        - All fields are required
        - Usernames must be unique
        - Students will be required to change their password on first login
        - Supervisors will be automatically created if they don't exist
        """)

    # Download sample CSV template
    sample_data = {
        "username": ["S12345", "S12346"],
        "name": ["John Doe", "Jane Smith"],
        "email": ["john.doe@university.edu", "jane.smith@university.edu"],
        "supervisor_name": ["Dr. Smith", "Dr. Jones"],
        "supervisor_email": ["dr.smith@university.edu", "dr.jones@university.edu"],
        "password": ["TempPass123", "TempPass456"]
    }
    sample_df = pd.DataFrame(sample_data)
    sample_csv = sample_df.to_csv(index=False)

    st.download_button(
        label="📥 Download Sample CSV Template",
        data=sample_csv,
        file_name="student_template.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file with student information"
    )

    if uploaded_file is not None:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)

            st.success(f"✅ File loaded successfully! Found {len(df)} students.")

            # Preview data
            st.subheader("Preview Data")
            st.dataframe(df, use_container_width=True)

            # Validate columns
            required_columns = ['username', 'name', 'email', 'supervisor_name', 'supervisor_email', 'password']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
            else:
                # Check for empty values
                if df.isnull().any().any():
                    st.warning("⚠️ Warning: Some cells are empty. Please ensure all fields are filled.")
                    st.dataframe(df[df.isnull().any(axis=1)], use_container_width=True)

                # Import button
                if st.button("Import Students", type="primary", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    success_count = 0
                    error_count = 0
                    errors = []

                    for index, row in df.iterrows():
                        try:
                            # Update progress
                            progress = (index + 1) / len(df)
                            progress_bar.progress(progress)
                            status_text.text(f"Processing {index + 1}/{len(df)}: {row['username']}")

                            # Create or get supervisor
                            get_or_create_supervisor(
                                email=row['supervisor_email'],
                                name=row['supervisor_name']
                            )

                            # Hash password
                            password_hash = hash_password(str(row['password']))

                            # Create student (assign to admin's department)
                            create_student(
                                username=str(row['username']),
                                password_hash=password_hash,
                                name=str(row['name']),
                                email=str(row['email']),
                                supervisor_email=str(row['supervisor_email']),
                                department=admin_dept
                            )

                            success_count += 1

                        except Exception as e:
                            error_count += 1
                            errors.append(f"Row {index + 1} ({row['username']}): {str(e)}")

                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()

                    # Show results
                    st.success(f"✅ Import complete! Successfully imported {success_count} students.")

                    if error_count > 0:
                        st.error(f"❌ {error_count} errors occurred:")
                        for error in errors:
                            st.write(f"- {error}")

                    st.balloons()

        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")

# TAB 2: View All Students
with tab2:
    if is_super_admin:
        st.subheader("All Registered Students (All Departments)")
    else:
        st.subheader(f"Students in {admin_dept} Department")

    try:
        # Filter students by department (unless super admin)
        if is_super_admin:
            students = get_all_students()  # Get all students
        else:
            students = get_all_students(department=admin_dept)  # Filter by department

        if not students:
            st.info(f"No students in {'the system' if is_super_admin else f'the {admin_dept} department'} yet. Upload a CSV to get started!")
        else:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Students", len(students))
            with col2:
                must_change = sum(1 for s in students if s.get('must_change_password', False))
                st.metric("Pending Password Change", must_change)
            with col3:
                unique_supervisors = len(set(s['supervisor_email'] for s in students))
                st.metric("Unique Supervisors", unique_supervisors)

            st.markdown("---")

            # Check if a student is selected
            if 'selected_student' not in st.session_state:
                st.session_state.selected_student = None

            # Show student list or detail view
            if st.session_state.selected_student is None:
                # LIST VIEW - Show all students with inline view buttons
                st.markdown("**Click 'View' button next to a student to see their submissions**")

                # CSS for table-like styling with borders using divs
                st.markdown("""
                <style>
                .student-row {
                    display: flex;
                    border: 1px solid #444;
                    border-top: none;
                    background-color: #0e1117;
                    height: 41px;
                    align-items: center;
                }
                .student-row:first-child {
                    border-top: 1px solid #444;
                }
                .student-header {
                    display: flex;
                    border: 1px solid #444;
                    background-color: #262730;
                    font-weight: bold;
                    color: #ffffff;
                    height: 41px;
                    align-items: center;
                }
                .table-col {
                    padding: 10px;
                    border-right: 1px solid #444;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                .table-col:last-child {
                    border-right: none;
                }
                .col-username { width: 20%; font-weight: bold; }
                .col-name { width: 25%; }
                .col-email { width: 27%; }
                .col-supervisor { width: 28%; }
                </style>
                """, unsafe_allow_html=True)

                # Create two main columns: table and buttons
                table_col, button_col = st.columns([9, 1])

                with table_col:
                    # Table header
                    st.markdown("""
                    <div class="student-header">
                        <div class="table-col col-username">Username</div>
                        <div class="table-col col-name">Name</div>
                        <div class="table-col col-email">Email</div>
                        <div class="table-col col-supervisor">Supervisor Email</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Student rows
                    for student in students:
                        st.markdown(f"""
                        <div class="student-row">
                            <div class="table-col col-username">{student['username']}</div>
                            <div class="table-col col-name">{student['name']}</div>
                            <div class="table-col col-email">{student['email']}</div>
                            <div class="table-col col-supervisor">{student['supervisor_email']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                with button_col:
                    # Add header spacing that matches the header height
                    st.markdown("""
                    <div style="height: 41px; display: flex; align-items: center; justify-content: center;
                                background-color: #262730; border: 1px solid #444; border-left: none;
                                font-weight: bold; color: #ffffff;">
                        View
                    </div>
                    """, unsafe_allow_html=True)

                    # Add view button for each student
                    for student in students:
                        if st.button("👁️", key=f"view_{student['username']}",
                                   help=f"View {student['username']}'s logs",
                                   use_container_width=True):
                            st.session_state.selected_student = student['username']
                            st.rerun()

                # Export option
                st.markdown("---")

                # Convert to DataFrame for export
                student_data = []
                for student in students:
                    student_data.append({
                        "Username": student['username'],
                        "Name": student['name'],
                        "Email": student['email'],
                        "Supervisor Email": student['supervisor_email'],
                        "Created": student['created_at'].strftime('%Y-%m-%d'),
                        "Must Change Password": "Yes" if student.get('must_change_password', False) else "No"
                    })

                df = pd.DataFrame(student_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Export Student List as CSV",
                    data=csv,
                    file_name="all_students.csv",
                    mime="text/csv"
                )

            else:
                # DETAIL VIEW - Show selected student's submissions
                from utils.database import get_student_by_username, get_student_logs

                selected_username = st.session_state.selected_student
                student = get_student_by_username(selected_username)

                if student is None:
                    st.error("Student not found!")
                    st.session_state.selected_student = None
                    st.rerun()
                else:
                    # Back button
                    if st.button("← Back to Student List"):
                        st.session_state.selected_student = None
                        st.rerun()

                    # Student info header
                    st.markdown(f"## 👤 {student['name']}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info(f"**Username:** {student['username']}")
                    with col2:
                        st.info(f"**Email:** {student['email']}")
                    with col3:
                        st.info(f"**Supervisor:** {student['supervisor_email']}")

                    st.markdown("---")

                    # Get student's logs
                    logs = get_student_logs(selected_username)

                    if not logs:
                        st.warning("This student hasn't submitted any logs yet.")
                    else:
                        # Log statistics
                        st.subheader(f"📊 Log Statistics ({len(logs)} total)")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Submissions", len(logs))
                        with col2:
                            approved = sum(1 for log in logs if log['verified'] == 'approved')
                            st.metric("Approved", approved)
                        with col3:
                            pending = sum(1 for log in logs if log['verified'] == 'pending')
                            st.metric("Pending", pending)
                        with col4:
                            rejected = sum(1 for log in logs if log['verified'] == 'rejected')
                            st.metric("Rejected", rejected)

                        st.markdown("---")

                        # Display logs
                        st.subheader("📝 All Submissions")

                        # Sort logs by week number (newest first)
                        sorted_logs = sorted(logs, key=lambda x: x['week_number'], reverse=True)

                        for log in sorted_logs:
                            # Status badge
                            if log['verified'] == 'approved':
                                status_emoji = "✅"
                                status_color = "green"
                            elif log['verified'] == 'rejected':
                                status_emoji = "❌"
                                status_color = "red"
                            else:
                                status_emoji = "⏳"
                                status_color = "orange"

                            # Create expandable card for each log
                            with st.expander(
                                f"{status_emoji} Week {log['week_number']} - {log['submitted_at'].strftime('%Y-%m-%d %H:%M')} - **{log['verified'].title()}**",
                                expanded=False
                            ):
                                col_detail1, col_detail2 = st.columns([3, 1])

                                with col_detail1:
                                    st.markdown("#### Log Content")
                                    st.markdown(f"""
                                    <div style="background-color: #1e1e1e; color: #e0e0e0; padding: 15px; border-radius: 5px; white-space: pre-wrap; border-left: 4px solid {status_color};">
{log['content']}
                                    </div>
                                    """, unsafe_allow_html=True)

                                with col_detail2:
                                    st.markdown("#### Details")
                                    st.write(f"**Week:** {log['week_number']}")
                                    st.write(f"**Submitted:** {log['submitted_at'].strftime('%Y-%m-%d %H:%M')}")
                                    st.write(f"**Status:** {status_emoji} {log['verified'].title()}")

                                    if log['verified'] == 'pending':
                                        st.info("Awaiting supervisor verification")
                                    elif log['verified'] == 'approved':
                                        st.success("Approved by supervisor")
                                    elif log['verified'] == 'rejected':
                                        st.error("Rejected by supervisor")

                        # Export student's logs
                        st.markdown("---")
                        if st.button("📥 Export This Student's Logs as CSV"):
                            export_data = []
                            for log in logs:
                                export_data.append({
                                    "Week Number": log['week_number'],
                                    "Submitted Date": log['submitted_at'].strftime('%Y-%m-%d %H:%M:%S'),
                                    "Status": log['verified'],
                                    "Content": log['content']
                                })

                            export_df = pd.DataFrame(export_data)
                            csv_data = export_df.to_csv(index=False)

                            st.download_button(
                                label=f"Download {student['name']}'s Logs",
                                data=csv_data,
                                file_name=f"logs_{selected_username}_{student['name'].replace(' ', '_')}.csv",
                                mime="text/csv"
                            )

    except Exception as e:
        st.error(f"Error loading students: {str(e)}")

# TAB 3: Test Email
with tab3:
    st.subheader("Test Email Configuration")

    st.info("""
    Use this to test if your email settings are configured correctly.
    An email will be sent to the address you specify.
    """)

    with st.form("test_email_form"):
        test_email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com"
        )

        send_test = st.form_submit_button("Send Test Email", type="primary")

        if send_test:
            if not test_email:
                st.error("Please enter an email address")
            else:
                from utils.email_sender import send_test_email

                success, message = send_test_email(test_email)

                if success:
                    st.success(message)
                else:
                    st.error(message)
                    st.info("""
                    **Common issues:**
                    - Gmail App Password not set in .env file
                    - GMAIL_USER not set in .env file
                    - 2-factor authentication not enabled on Gmail account
                    - App Password not generated in Google Account settings

                    See the setup instructions for help.
                    """)
