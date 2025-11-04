"""
Change Password Page

Allows students to update their password.
"""

import streamlit as st
from utils.auth import require_login, get_current_user, verify_password
from utils.database import get_student_by_username, update_student_password
from utils.auth import hash_password

st.set_page_config(
    page_title="Change Password",
    page_icon="🔐",
    layout="wide"
)

# Require login
require_login()

st.title("🔐 Change Password")
st.markdown("Update your account password for security")
st.markdown("---")

# Get current user
username = get_current_user()
student = get_student_by_username(username)

# Check if password change is required
if student.get('must_change_password', False):
    st.warning("""
    ⚠️ **Password Change Required**

    You are using a temporary password. For security reasons, you must change
    your password before continuing to use the system.
    """)

# Password requirements info
with st.expander("📋 Password Requirements", expanded=False):
    st.markdown("""
    Your new password must meet the following criteria:

    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Different from your current password

    **Tips for a strong password:**
    - Use a mix of letters, numbers, and symbols
    - Avoid common words or patterns
    - Don't use personal information (birthdate, name, etc.)
    - Consider using a passphrase (e.g., "Coffee!Morning2024")
    """)

# Main form
col1, col2 = st.columns([2, 1])

with col1:
    with st.form("change_password_form"):
        st.subheader("Enter New Password")

        current_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter your current password"
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter your new password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter your new password"
        )

        submit_button = st.form_submit_button(
            "Change Password",
            type="primary",
            use_container_width=True
        )

        if submit_button:
            # Validation
            errors = []

            # Check if all fields are filled
            if not current_password or not new_password or not confirm_password:
                errors.append("All fields are required")

            # Verify current password
            if current_password and not verify_password(current_password, student['password']):
                errors.append("Current password is incorrect")

            # Check if new passwords match
            if new_password != confirm_password:
                errors.append("New passwords do not match")

            # Check if new password is different from current
            if current_password == new_password:
                errors.append("New password must be different from current password")

            # Password strength validation
            if len(new_password) < 8:
                errors.append("Password must be at least 8 characters long")

            if not any(c.isupper() for c in new_password):
                errors.append("Password must contain at least one uppercase letter")

            if not any(c.islower() for c in new_password):
                errors.append("Password must contain at least one lowercase letter")

            if not any(c.isdigit() for c in new_password):
                errors.append("Password must contain at least one number")

            # Display errors or update password
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    # Hash new password and update
                    new_password_hash = hash_password(new_password)
                    success = update_student_password(username, new_password_hash)

                    if success:
                        st.success("""
                        ✅ Password changed successfully!

                        Your password has been updated. Please use your new password
                        for future logins.
                        """)
                        st.balloons()

                        # Update session state
                        st.session_state['must_change_password'] = False
                    else:
                        st.error("Failed to update password. Please try again.")

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

with col2:
    st.subheader("🛡️ Security Tips")

    st.info("""
    **Keep Your Account Safe**

    ✓ Never share your password
    ✓ Use a unique password
    ✓ Change it regularly
    ✓ Log out on shared devices
    """)

    st.markdown("---")

    st.subheader("📊 Account Info")
    st.write(f"**Username**: {username}")
    st.write(f"**Name**: {student['name']}")
    st.write(f"**Email**: {student['email']}")

    if student.get('must_change_password', False):
        st.error("⚠️ Password change required")
    else:
        st.success("✅ Account is secure")
