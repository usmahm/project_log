"""
Super Admin Page

This page is only accessible to super admins.
Allows creation and management of department admins.
"""

import streamlit as st
import pandas as pd
from utils.auth import require_super_admin, hash_password, get_current_admin
from utils.database import create_admin, get_all_admins

st.set_page_config(
    page_title="Super Admin",
    page_icon="⭐",
    layout="wide"
)

# Require super admin access
require_super_admin()

st.title("⭐ Super Admin Panel")
st.markdown("Manage department administrators")
st.markdown("---")

# Tabs for different functions
tab1, tab2 = st.tabs(["➕ Create Department Admin", "👥 View All Admins"])

# TAB 1: Create Department Admin
with tab1:
    st.subheader("Create New Department Admin")

    st.info("""
    Department admins can:
    - Upload and manage students in their department
    - View student submissions for their department only
    - Cannot create other admins
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("create_admin_form"):
            st.markdown("### Admin Details")

            admin_username = st.text_input(
                "Admin Username",
                placeholder="e.g., admin_cs, admin_eng",
                help="Unique username for the admin"
            )

            admin_name = st.text_input(
                "Full Name",
                placeholder="e.g., Dr. John Smith"
            )

            admin_email = st.text_input(
                "Email Address",
                placeholder="admin@university.edu"
            )

            admin_department = st.text_input(
                "Department Code",
                placeholder="e.g., CS, ENG, BIO, MATH",
                help="Department this admin will manage"
            )

            temp_password = st.text_input(
                "Temporary Password",
                type="password",
                placeholder="Enter temporary password",
                help="Admin will be required to change this on first login"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter password"
            )

            submit_button = st.form_submit_button(
                "Create Department Admin",
                type="primary",
                use_container_width=True
            )

            if submit_button:
                # Validation
                errors = []

                if not admin_username or not admin_name or not admin_email or not admin_department or not temp_password:
                    errors.append("All fields are required")

                if temp_password != confirm_password:
                    errors.append("Passwords do not match")

                if len(temp_password) < 5:
                    errors.append("Password must be at least 5 characters")

                # Check if username already exists
                from utils.database import get_admin_by_username
                if get_admin_by_username(admin_username):
                    errors.append(f"Admin username '{admin_username}' already exists")

                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    try:
                        # Hash password and create admin
                        password_hash = hash_password(temp_password)

                        admin_id = create_admin(
                            username=admin_username,
                            password_hash=password_hash,
                            name=admin_name,
                            email=admin_email,
                            department=admin_department.upper(),
                            role="department_admin"
                        )

                        st.success(f"""
                        ✅ Department Admin created successfully!

                        **Username:** {admin_username}
                        **Department:** {admin_department.upper()}

                        The admin can now log in using the Admin Login page.
                        They will be required to change their password on first login.
                        """)
                        st.balloons()

                    except Exception as e:
                        st.error(f"Failed to create admin: {str(e)}")

    with col2:
        st.markdown("### 💡 Tips")
        st.info("""
        **Username Convention:**
        - Use descriptive names
        - Include department code
        - Examples:
          - admin_cs
          - admin_engineering
          - cs_admin

        **Department Codes:**
        - Keep them short
        - Use uppercase
        - Be consistent
        """)

# TAB 2: View All Admins
with tab2:
    st.subheader("All Administrators")

    try:
        admins = get_all_admins()

        if not admins:
            st.info("No department admins created yet.")
        else:
            # Summary metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                total_admins = len(admins)
                st.metric("Total Admins", total_admins)

            with col2:
                super_admins = len([a for a in admins if a['role'] == 'super_admin'])
                st.metric("Super Admins", super_admins)

            with col3:
                dept_admins = len([a for a in admins if a['role'] == 'department_admin'])
                st.metric("Department Admins", dept_admins)

            st.markdown("---")

            # Department filter
            departments = sorted(set(a['department'] for a in admins))
            dept_filter = st.selectbox(
                "Filter by Department",
                options=["All"] + departments
            )

            # Filter admins
            filtered_admins = admins if dept_filter == "All" else [a for a in admins if a['department'] == dept_filter]

            st.markdown(f"**Showing {len(filtered_admins)} admin(s)**")
            st.markdown("---")

            # Display admin list
            admin_data = []
            for admin in filtered_admins:
                role_display = "Super Admin" if admin['role'] == 'super_admin' else "Department Admin"
                admin_data.append({
                    "Username": admin['username'],
                    "Name": admin['name'],
                    "Email": admin['email'],
                    "Department": admin['department'],
                    "Role": role_display,
                    "Created": admin['created_at'].strftime('%Y-%m-%d'),
                    "Must Change Password": "Yes" if admin.get('must_change_password', False) else "No"
                })

            df = pd.DataFrame(admin_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # Export option
            st.markdown("---")
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Export Admin List as CSV",
                data=csv,
                file_name="all_admins.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error loading admins: {str(e)}")
