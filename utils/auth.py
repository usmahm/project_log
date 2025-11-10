"""
Authentication utilities for login and password management.

This module handles password hashing, verification, and user authentication.
"""

import bcrypt
import streamlit as st
from utils.database import get_student_by_username, get_admin_by_username


def hash_password(password):
    """
    Hashes a password using bcrypt.

    Why bcrypt? It's designed for passwords and automatically handles salting.
    Salting means even if two users have the same password, the hashes differ.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    # Convert password to bytes and hash it
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password, hashed_password):
    """
    Verifies a password against its hash.

    Args:
        password: Plain text password to verify
        hashed_password: Stored hashed password

    Returns:
        bool: True if password matches
    """
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def authenticate_user(username, password):
    """
    Authenticates a user by username and password.

    Args:
        username: Student's username
        password: Plain text password

    Returns:
        dict: Student document if authenticated, None otherwise
    """
    student = get_student_by_username(username)

    if student and verify_password(password, student['password']):
        return student
    return None


def login_user(username, password):
    """
    Logs in a user and stores their info in Streamlit session state.

    Streamlit Session State: Think of it as memory that persists across
    page refreshes and navigation. Without it, Streamlit would "forget"
    the user is logged in when they click to another page!

    Args:
        username: Student's username
        password: Plain text password

    Returns:
        tuple: (success: bool, message: str)
    """
    student = authenticate_user(username, password)

    if student:
        # Store user info in session state
        st.session_state['logged_in'] = True
        st.session_state['username'] = student['username']
        st.session_state['student_name'] = student['name']
        st.session_state['must_change_password'] = student.get('must_change_password', False)

        return True, "Login successful!"
    else:
        return False, "Invalid username or password"


def logout_user():
    """
    Logs out the current user by clearing session state.
    """
    # Clear all session state variables
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def is_logged_in():
    """
    Checks if a user is currently logged in.

    Returns:
        bool: True if user is logged in
    """
    return st.session_state.get('logged_in', False)


def get_current_user():
    """
    Gets the current logged-in user's username.

    Returns:
        str: Username or None if not logged in
    """
    return st.session_state.get('username', None)


def require_login():
    """
    Decorator-like function to require login for a page.

    Use this at the top of pages that need authentication.

    Returns:
        bool: True if user is logged in, False otherwise
    """
    if not is_logged_in():
        st.warning("Please log in to access this page")
        st.stop()  # Stops execution of the rest of the page
        return False
    return True


# Admin authentication functions
def authenticate_admin(username, password):
    """
    Authenticates an admin by username and password.

    Args:
        username: Admin's username
        password: Plain text password

    Returns:
        dict: Admin document if authenticated, None otherwise
    """
    admin = get_admin_by_username(username)

    if admin and verify_password(password, admin['password']):
        return admin
    return None


def login_admin(username, password):
    """
    Logs in an admin and stores their info in Streamlit session state.

    Args:
        username: Admin's username
        password: Plain text password

    Returns:
        tuple: (success: bool, message: str)
    """
    admin = authenticate_admin(username, password)

    if admin:
        # Store admin info in session state
        st.session_state['admin_logged_in'] = True
        st.session_state['admin_username'] = admin['username']
        st.session_state['admin_name'] = admin['name']
        st.session_state['admin_department'] = admin['department']
        st.session_state['admin_role'] = admin['role']
        st.session_state['admin_must_change_password'] = admin.get('must_change_password', False)

        return True, "Admin login successful!"
    else:
        return False, "Invalid admin username or password"


def logout_admin():
    """
    Logs out the current admin by clearing admin session state.
    """
    # Clear admin session state variables
    admin_keys = ['admin_logged_in', 'admin_username', 'admin_name',
                  'admin_department', 'admin_role', 'admin_must_change_password']
    for key in admin_keys:
        if key in st.session_state:
            del st.session_state[key]


def is_admin_logged_in():
    """
    Checks if an admin is currently logged in.

    Returns:
        bool: True if admin is logged in
    """
    return st.session_state.get('admin_logged_in', False)


def get_current_admin():
    """
    Gets the current logged-in admin's username.

    Returns:
        str: Admin username or None if not logged in
    """
    return st.session_state.get('admin_username', None)


def get_admin_role():
    """
    Gets the current admin's role.

    Returns:
        str: 'super_admin' or 'department_admin', or None if not logged in
    """
    return st.session_state.get('admin_role', None)


def get_admin_department():
    """
    Gets the current admin's department.

    Returns:
        str: Department code or None if not logged in
    """
    return st.session_state.get('admin_department', None)


def require_admin_login():
    """
    Requires admin login for a page.

    Use this at the top of admin pages.

    Returns:
        bool: True if admin is logged in, False otherwise
    """
    if not is_admin_logged_in():
        st.warning("⚠️ Admin access required. Please log in as an administrator.")
        st.stop()
        return False
    return True


def require_super_admin():
    """
    Requires super admin role for a page.

    Returns:
        bool: True if user is super admin, False otherwise
    """
    if not is_admin_logged_in():
        st.error("⚠️ Admin access required")
        st.stop()
        return False

    if get_admin_role() != 'super_admin':
        st.error("⚠️ Super Admin access required. You don't have permission to access this page.")
        st.stop()
        return False

    return True
