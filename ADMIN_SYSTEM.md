# Admin System Overview

This document explains the new admin authentication and department isolation system.

## What Changed?

### Before:
- No admin authentication
- Anyone could access the Admin page
- All students in one pool

### Now:
- ✅ Admins must log in
- ✅ Two-tier admin system (Super Admin + Department Admins)
- ✅ Students organized by department
- ✅ Department admins can only see their department's students

## Admin Roles

### 1. Super Admin
**Username Example:** `superadmin`
**Department:** ALL

**Capabilities:**
- Create department admins
- View ALL students across ALL departments
- Full system access
- Access to Super Admin page

**How to create:** Run `python create_super_admin.py`

### 2. Department Admin
**Username Example:** `admin_cs`, `admin_eng`
**Department:** CS, ENG, BIO, etc.

**Capabilities:**
- Upload students (automatically assigned to their department)
- View only their department's students
- Cannot create other admins
- Cannot see other departments

**How to create:** Super admin creates them via Super Admin page

## Database Changes

### New Collection: `admins`
```python
{
    "username": "admin_cs",
    "password": "hashed_password",
    "name": "Dr. John Smith",
    "email": "john.smith@university.edu",
    "department": "CS",
    "role": "department_admin",  # or "super_admin"
    "created_at": datetime,
    "must_change_password": True
}
```

### Updated Collection: `students`
```python
{
    "username": "S12345",
    "password": "hashed_password",
    "name": "Jane Doe",
    "email": "jane@university.edu",
    "supervisor_email": "supervisor@university.edu",
    "department": "CS",  # NEW FIELD
    "created_at": datetime,
    "must_change_password": True
}
```

## New Pages

### 6. Admin Login (`pages/6_🔑_Admin_Login.py`)
- Separate login for administrators
- Shows admin dashboard with role info
- Logout functionality

### 7. Super Admin (`pages/7_⭐_Super_Admin.py`)
- Only accessible to super admins
- Create department admins
- View all admins
- Export admin list

## Updated Pages

### 4. Admin Panel (`pages/4_👨‍💼_Admin.py`)
- Now requires admin authentication
- Filters students by department (unless super admin)
- Shows department info in header
- Students uploaded are automatically assigned to admin's department

## Setup Flow

1. **Initial Setup**
   ```bash
   python create_super_admin.py
   ```
   - Creates first super admin account
   - Username: superadmin (or custom)
   - Department: ALL
   - Role: super_admin

2. **Super Admin Creates Department Admins**
   - Login as super admin
   - Go to Super Admin page
   - Create admin for CS department
   - Create admin for ENG department
   - etc.

3. **Department Admins Manage Students**
   - CS admin logs in
   - Uploads CS students via CSV
   - All uploaded students automatically tagged with "CS" department
   - CS admin can only see CS students

4. **Department Isolation**
   - CS admin cannot see ENG students
   - ENG admin cannot see CS students
   - Super admin can see all students

## Authentication Functions

### For Admins (in `utils/auth.py`)
```python
login_admin(username, password)  # Admin login
logout_admin()                   # Admin logout
is_admin_logged_in()            # Check admin session
get_current_admin()             # Get admin username
get_admin_role()                # Get 'super_admin' or 'department_admin'
get_admin_department()          # Get admin's department
require_admin_login()           # Protect admin pages
require_super_admin()           # Protect super admin pages
```

### For Students (existing, unchanged)
```python
login_user(username, password)  # Student login
logout_user()                   # Student logout
is_logged_in()                  # Check student session
get_current_user()              # Get student username
require_login()                 # Protect student pages
```

## Database Functions

### Admin Operations (in `utils/database.py`)
```python
create_admin(username, password_hash, name, email, department, role)
get_admin_by_username(username)
get_all_admins(department=None)  # Optional filter
update_admin_password(username, new_password_hash)
```

### Student Operations (updated)
```python
create_student(..., department="CS")  # Now includes department
get_all_students(department=None)     # Now supports filtering
```

## Testing the System

1. **Create Super Admin**
   ```bash
   python create_super_admin.py
   ```

2. **Test Super Admin Login**
   - Go to Admin Login page
   - Login with super admin credentials
   - Verify access to Super Admin page
   - Verify can see all students

3. **Create Department Admin**
   - As super admin, go to Super Admin page
   - Create admin for "CS" department
   - Username: admin_cs
   - Department: CS

4. **Test Department Admin Login**
   - Logout super admin
   - Login as admin_cs
   - Go to Admin Panel
   - Upload CSV with students
   - Verify students are tagged with "CS"
   - Verify can only see CS students

5. **Test Department Isolation**
   - Create another department admin (ENG)
   - Upload students as ENG admin
   - Login as CS admin
   - Verify cannot see ENG students

## Migration for Existing Students

If you already have students in the database without department field:

```python
# Run this in a Python script or MongoDB shell
from utils.database import get_database

db = get_database()
db.students.update_many(
    {"department": {"$exists": False}},
    {"$set": {"department": "general"}}
)
```

This assigns all existing students to a "general" department.

## Security Notes

- Admin and student sessions are separate
- Admin cannot access student pages without student login
- Students cannot access admin pages
- Department admins strictly isolated by department
- Only super admin can create admins
- All passwords hashed with bcrypt
- Forced password change on first login for all users

## Future Enhancements

Potential improvements:
- Admin password reset via email
- Department admin can change their own department students' passwords
- Audit log for admin actions
- Bulk department transfer for students
- Department-specific settings
