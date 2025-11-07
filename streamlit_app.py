"""
Project Logging System - Main Application

This is the entry point of the application.
Students log in here to access their dashboard.
"""

import streamlit as st
from utils.auth import login_user, logout_user, is_logged_in

# Streamlit page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="Project Logging System",
    page_icon="📝",
    layout="wide",  # Use full width of the page
    initial_sidebar_state="expanded"
)


def show_login_page():
    """
    Displays the login page with username and password fields.
    """
    st.title("📝 Project Logging System")
    st.markdown("### Student Login")

    # Create a centered column layout
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Login form
        with st.form("login_form"):
            st.write("Please enter your credentials to continue")

            username = st.text_input("Username", placeholder="Enter your student ID")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            submit_button = st.form_submit_button("Login", use_container_width=True)

            if submit_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    # Attempt login
                    success, message = login_user(username, password)

                    if success:
                        st.success(message)
                        st.rerun()  # Refresh the page to show logged-in view
                    else:
                        print("message", message)
                        st.error(message)

        # Information box
        st.info("""
        **First time logging in?**

        Your account has been created by your administrator.
        - Username: Your student ID
        - Password: Temporary password provided by admin
        - You'll be asked to change your password after first login
        """)


def show_dashboard():
    """
    Displays the main dashboard for logged-in students.
    """
    st.title(f"Welcome, {st.session_state.get('student_name', 'Student')}!")

    # Check if password change is required
    if st.session_state.get('must_change_password', False):
        st.warning("⚠️ You must change your password before continuing. Please visit the Change Password page.")

    st.markdown("---")

    # Quick stats/info cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📝 **Submit Log**\n\nSubmit your weekly project update")

    with col2:
        st.info("📋 **View Logs**\n\nReview your submission history")

    with col3:
        st.info("🔐 **Change Password**\n\nUpdate your account password")

    st.markdown("---")

    # Instructions
    st.markdown("""
    ### How to use this system:

    1. **Submit Weekly Logs**: Navigate to "Submit Log" page to enter your weekly project updates
    2. **Track Progress**: View all your previous submissions and their verification status
    3. **Automatic Notifications**: Your supervisor receives an email automatically when you submit
    4. **Verification**: Supervisors can approve or reject your logs via email

    Use the sidebar to navigate between different sections.
    """)

    # Logout button
    if st.button("Logout", type="secondary"):
        logout_user()
        st.rerun()


def main():
    """
    Main application logic.

    This function decides what to show based on login status.
    """
    # Sidebar
    with st.sidebar:
        # st.image("https://via.placeholder.com/150x50/3498db/ffffff?text=Logo", use_container_width=True)

        if is_logged_in():
            st.success(f"Logged in as: {st.session_state.get('username')}")
            st.markdown("---")
            st.markdown("### Navigation")
            st.info("Use the pages menu above to navigate")
        else:
            st.info("Please log in to access the system")

    # Main content
    if is_logged_in():
        show_dashboard()
    else:
        show_login_page()


# Run the application
if __name__ == "__main__":
    main()