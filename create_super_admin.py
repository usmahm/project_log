"""
Setup Script: Create Super Admin

This script creates the initial super admin account.
Run this ONCE when setting up the system for the first time.

Usage:
    python create_super_admin.py
"""

import sys
from utils.auth import hash_password
from utils.database import create_admin, get_admin_by_username


def create_super_admin():
    """
    Creates the initial super admin account.
    """
    print("=" * 50)
    print("SUPER ADMIN CREATION SCRIPT")
    print("=" * 50)
    print()

    # Check if super admin already exists
    print("Checking for existing super admin...")
    existing_admin = get_admin_by_username("superadmin")

    if existing_admin:
        print("⚠️  WARNING: Super admin 'superadmin' already exists!")
        response = input("Do you want to continue anyway? This will create a duplicate. (yes/no): ")
        if response.lower() != "yes":
            print("Setup cancelled.")
            return

    print()
    print("Create your super admin account:")
    print("-" * 50)

    # Get admin details
    username = input("Enter super admin username (default: superadmin): ").strip()
    if not username:
        username = "superadmin"

    name = input("Enter super admin full name: ").strip()
    if not name:
        print("❌ Name cannot be empty!")
        sys.exit(1)

    email = input("Enter super admin email: ").strip()
    if not email:
        print("❌ Email cannot be empty!")
        sys.exit(1)

    # Get password
    while True:
        password = input("Enter super admin password (min 5 characters): ").strip()
        if len(password) < 5:
            print("❌ Password must be at least 5 characters!")
            continue

        confirm_password = input("Confirm password: ").strip()
        if password != confirm_password:
            print("❌ Passwords do not match!")
            continue

        break

    # Confirm creation
    print()
    print("-" * 50)
    print("REVIEW SUPER ADMIN DETAILS:")
    print(f"  Username: {username}")
    print(f"  Name: {name}")
    print(f"  Email: {email}")
    print(f"  Role: Super Admin")
    print(f"  Department: ALL")
    print("-" * 50)

    confirm = input("Create this super admin account? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Setup cancelled.")
        return

    try:
        # Hash password
        password_hash = hash_password(password)

        # Create super admin
        admin_id = create_admin(
            username=username,
            password_hash=password_hash,
            name=name,
            email=email,
            department="ALL",
            role="super_admin"
        )

        print()
        print("✅ SUCCESS! Super admin created successfully!")
        print()
        print("You can now:")
        print("  1. Start the Streamlit app: streamlit run streamlit_app.py")
        print("  2. Navigate to the 'Admin Login' page")
        print(f"  3. Login with username: {username}")
        print("  4. You will be required to change your password on first login")
        print()
        print("As a super admin, you can:")
        print("  - Create department admins (Super Admin page)")
        print("  - View all students across all departments (Admin Panel)")
        print("  - Manage the entire system")
        print()

    except Exception as e:
        print(f"❌ ERROR: Failed to create super admin: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        create_super_admin()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)
