"""
Admin Page

This page allows administrators to upload student data via CSV.
For simplicity, this page doesn't require separate admin authentication.
In production, you'd want proper admin authentication.
"""

import streamlit as st
import pandas as pd
from utils.auth import hash_password
from utils.database import create_student, get_or_create_supervisor, get_all_students

st.set_page_config(
    page_title="Admin Panel",
    page_icon="👨‍💼",
    layout="wide"
)

st.title("👨‍💼 Admin Panel")
st.markdown("Upload student data and manage the system")
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

                            # Create student
                            create_student(
                                username=str(row['username']),
                                password_hash=password_hash,
                                name=str(row['name']),
                                email=str(row['email']),
                                supervisor_email=str(row['supervisor_email'])
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
    st.subheader("All Registered Students")

    try:
        students = get_all_students()

        if not students:
            st.info("No students in the system yet. Upload a CSV to get started!")
        else:
            # Convert to DataFrame for display
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

            # Display table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # Export option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Export Student List as CSV",
                data=csv,
                file_name="all_students.csv",
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
