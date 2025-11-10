"""
Database utility for MongoDB operations.

This module handles all database connections and CRUD operations.
"""

import streamlit as st
from datetime import datetime
from pymongo import MongoClient

# MongoDB connection
def get_database():
    """
    Creates and returns a MongoDB database connection.

    Returns:
        database: MongoDB database object
    """
    # Get MongoDB URI from Streamlit secrets
    try:
        mongodb_uri = st.secrets["MONGODB_URI"]
    except (KeyError, FileNotFoundError):
        raise ValueError("MONGODB_URI not found in Streamlit secrets. Please configure secrets.toml")

    # Create MongoDB client
    client = MongoClient(mongodb_uri)

    # Return the database (named 'project_logs')
    return client['project_logs']


# Admin operations
def create_admin(username, password_hash, name, email, department, role="department_admin"):
    """
    Creates a new admin in the database.

    Args:
        username: Admin's unique username
        password_hash: Hashed password
        name: Admin's full name
        email: Admin's email address
        department: Department code/name (e.g., "CS", "ENG", "BIO")
        role: Either "super_admin" or "department_admin"

    Returns:
        str: The inserted admin's ID
    """
    db = get_database()

    admin_data = {
        "username": username,
        "password": password_hash,
        "name": name,
        "email": email,
        "department": department,
        "role": role,  # super_admin or department_admin
        "created_at": datetime.now(),
        "must_change_password": True
    }

    result = db.admins.insert_one(admin_data)
    return str(result.inserted_id)


def get_admin_by_username(username):
    """
    Retrieves an admin by their username.

    Args:
        username: The admin's username

    Returns:
        dict: Admin document or None if not found
    """
    db = get_database()
    return db.admins.find_one({"username": username})


def get_all_admins(department=None):
    """
    Retrieves all admins, optionally filtered by department.

    Args:
        department: Optional department filter

    Returns:
        list: List of admin documents
    """
    db = get_database()
    query = {"department": department} if department else {}
    return list(db.admins.find(query))


def update_admin_password(username, new_password_hash):
    """
    Updates an admin's password.

    Args:
        username: Admin's username
        new_password_hash: New hashed password

    Returns:
        bool: True if updated successfully
    """
    db = get_database()
    result = db.admins.update_one(
        {"username": username},
        {
            "$set": {
                "password": new_password_hash,
                "must_change_password": False
            }
        }
    )
    return result.modified_count > 0


# Student operations
def create_student(username, password_hash, name, email, supervisor_email, department="general"):
    """
    Creates a new student in the database.

    Args:
        username: Student's unique username (e.g., student ID)
        password_hash: Hashed password (never store plain passwords!)
        name: Student's full name
        email: Student's email address
        supervisor_email: Email of assigned supervisor
        department: Department code/name (defaults to "general")

    Returns:
        str: The inserted student's ID
    """
    db = get_database()

    student_data = {
        "username": username,
        "password": password_hash,
        "name": name,
        "email": email,
        "supervisor_email": supervisor_email,
        "department": department,
        "created_at": datetime.now(),
        "must_change_password": True  # Force password change on first login
    }

    result = db.students.insert_one(student_data)
    return str(result.inserted_id)


def get_student_by_username(username):
    """
    Retrieves a student by their username.

    Args:
        username: The student's username

    Returns:
        dict: Student document or None if not found
    """
    db = get_database()
    return db.students.find_one({"username": username})


def update_student_password(username, new_password_hash):
    """
    Updates a student's password.

    Args:
        username: Student's username
        new_password_hash: New hashed password

    Returns:
        bool: True if updated successfully
    """
    db = get_database()
    result = db.students.update_one(
        {"username": username},
        {
            "$set": {
                "password": new_password_hash,
                "must_change_password": False
            }
        }
    )
    return result.modified_count > 0


# Log operations
def create_log(student_username, week_number, content):
    """
    Creates a new weekly log entry.

    Args:
        student_username: Username of the student
        week_number: Week number (1-52)
        content: The log content

    Returns:
        str: The inserted log's ID
    """
    db = get_database()

    # Get student info
    student = get_student_by_username(student_username)
    if not student:
        raise ValueError("Student not found")

    log_data = {
        "student_username": student_username,
        "student_name": student["name"],
        "student_email": student["email"],
        "supervisor_email": student["supervisor_email"],
        "week_number": week_number,
        "content": content,
        "submitted_at": datetime.now(),
        "verified": "pending",  # pending, approved, rejected
        "verification_token": None  # Will be set when email is sent
    }

    result = db.logs.insert_one(log_data)
    return str(result.inserted_id)


def get_student_logs(student_username):
    """
    Retrieves all logs for a specific student, sorted by week number.

    Args:
        student_username: Username of the student

    Returns:
        list: List of log documents
    """
    db = get_database()
    logs = db.logs.find({"student_username": student_username}).sort("week_number", -1)
    return list(logs)


def get_log_by_id(log_id):
    """
    Retrieves a specific log by its ID.

    Args:
        log_id: The log's ObjectId as string

    Returns:
        dict: Log document or None
    """
    from bson.objectid import ObjectId
    db = get_database()
    return db.logs.find_one({"_id": ObjectId(log_id)})


def update_log_verification_token(log_id, token):
    """
    Updates a log with its verification token.

    Args:
        log_id: The log's ID
        token: Verification token
    """
    from bson.objectid import ObjectId
    db = get_database()
    db.logs.update_one(
        {"_id": ObjectId(log_id)},
        {"$set": {"verification_token": token}}
    )


def verify_log(token, status):
    """
    Verifies or rejects a log using the token.

    Args:
        token: Verification token from email link
        status: 'approved' or 'rejected'

    Returns:
        dict: Updated log or None if token invalid
    """
    db = get_database()
    log = db.logs.find_one({"verification_token": token})

    if log:
        db.logs.update_one(
            {"verification_token": token},
            {"$set": {"verified": status}}
        )
        return log
    return None


# Supervisor operations
def get_or_create_supervisor(email, name=None):
    """
    Gets an existing supervisor or creates a new one.

    Args:
        email: Supervisor's email
        name: Supervisor's name (optional)

    Returns:
        dict: Supervisor document
    """
    db = get_database()
    supervisor = db.supervisors.find_one({"email": email})

    if not supervisor:
        supervisor_data = {
            "email": email,
            "name": name or email.split('@')[0],  # Use email prefix if no name
            "created_at": datetime.now()
        }
        db.supervisors.insert_one(supervisor_data)
        supervisor = supervisor_data

    return supervisor


# Admin operations
def get_all_students(department=None):
    """
    Retrieves all students for admin view, optionally filtered by department.

    Args:
        department: Optional department filter

    Returns:
        list: List of student documents
    """
    db = get_database()
    query = {"department": department} if department else {}
    return list(db.students.find(query))


def check_existing_log(student_username, week_number):
    """
    Checks if a student has already submitted a log for a specific week.

    Args:
        student_username: Student's username
        week_number: Week number to check

    Returns:
        dict: Existing log or None
    """
    db = get_database()
    return db.logs.find_one({
        "student_username": student_username,
        "week_number": week_number
    })
