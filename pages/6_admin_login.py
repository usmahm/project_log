"""
Admin Login Page

Separate login page for administrators (both super admin and department admins).
"""

import streamlit as st
from utils.auth import login_admin, is_admin_logged_in, logout_admin, get_admin_role, get_current_admin

st.set_page_config(
    page_title="Admin Login",
    page_icon="🔑",
    layout="wide"
)

# Check if already logged in
if is_admin_logged_in():
    st.title("🔑 Admin Dashboard")
    st.success(f"Welcome back, {st.session_state.get('admin_name', 'Admin')}!")

    # Display admin info
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"**Username:** {get_current_admin()}")
    with col2:
        role = get_admin_role()
        role_display = "Super Admin" if role == "super_admin" else "Department Admin"
        st.info(f"**Role:** {role_display}")
    with col3:
        dept = st.session_state.get('admin_department', 'N/A')
        st.info(f"**Department:** {dept}")

    st.markdown("---")

    # Quick links
    st.subheader("Quick Links")

    col1, col2 = st.columns(2)

    with col1:
        if role == "super_admin":
            st.markdown("### Super Admin")
            st.markdown("- Navigate to **Super Admin** page to create department admins")
        st.markdown("- Navigate to **Admin Panel** to manage students")

    with col2:
        st.markdown("### Account")
        if st.button("🔓 Logout", use_container_width=True):
            logout_admin()
            st.success("Logged out successfully!")
            st.rerun()

else:
    # Login form
    st.title("🔑 Admin Login")
    st.markdown("Administrator access required")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("admin_login_form"):
            st.subheader("Enter Admin Credentials")

            username = st.text_input(
                "Admin Username",
                placeholder="Enter your admin username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            submit_button = st.form_submit_button(
                "Login as Admin",
                type="primary",
                use_container_width=True
            )

            if submit_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    success, message = login_admin(username, password)

                    if success:
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)

    with col2:
        st.info("""
        **Admin Access**

        This portal is for administrators only.

        - **Super Admins**: Can create department admins
        - **Department Admins**: Can manage students in their department

        Students should use the main login page.
        """)

        st.markdown("---")

        st.caption("Need help? Contact your system administrator.")
