# 📝 Project Logging System

A Streamlit-based web application for students to submit weekly project logs, with automatic email notifications to supervisors for verification.

## Features

- **Student Authentication** - Secure login with password hashing
- **Weekly Log Submission** - Students submit project updates with automatic week tracking
- **Email Verification** - Supervisors receive emails with one-click approve/reject buttons
- **Log History** - Students can view all their submissions and verification status
- **Password Management** - Forced password change on first login, with strength validation
- **Admin Panel** - Bulk import students via CSV upload
- **MongoDB Backend** - Scalable NoSQL database

## Technology Stack

- **Frontend**: Streamlit
- **Database**: MongoDB (Atlas)
- **Email**: Gmail SMTP
- **Security**: bcrypt password hashing
- **Data Processing**: pandas

## Prerequisites

1. **Python 3.8+**
2. **MongoDB Atlas Account** (free tier works) - [Sign up here](https://www.mongodb.com/cloud/atlas/register)
3. **Gmail Account** with 2-factor authentication and App Password

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up MongoDB Atlas

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Create a free account and cluster
3. Click "Connect" → "Connect your application"
4. Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/...`)
5. Replace `<password>` with your database password
6. Replace `<dbname>` with `project_logs`

### 3. Set Up Gmail App Password

Since Google requires 2-factor authentication for apps, you need an "App Password":

1. Enable 2-factor authentication on your Gmail account:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Turn on "2-Step Verification"

2. Generate App Password:
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Other (Custom name)"
   - Name it "Project Logging System"
   - Copy the 16-character password

### 4. Configure Secrets (Streamlit Secrets Management)

Streamlit uses a special `secrets.toml` file for managing sensitive configuration.

1. Create the secrets file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` and fill in your credentials:
   ```toml
   MONGODB_URI = "mongodb+srv://your-username:your-password@cluster.mongodb.net/project_logs?retryWrites=true&w=majority"
   GMAIL_USER = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "your-16-char-app-password"
   APP_URL = "http://localhost:8501"
   SECRET_KEY = "your-random-secret-key-here"
   ```

   **Notes**:
   - For `SECRET_KEY`, generate a random string: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Never commit `secrets.toml` to git (it's already in `.gitignore`)
   - When deployed to Streamlit Community Cloud, paste these secrets in the app settings

### 5. Run the Application

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Quick Start Guide

### Initial Setup (Super Admin)

1. **Create the first super admin account:**
   ```bash
   python create_super_admin.py
   ```
   Follow the prompts to create your super admin credentials.

2. **Login as Super Admin:**
   - Navigate to "Admin Login" page
   - Use your super admin credentials
   - Change password on first login

3. **Create Department Admins:**
   - Go to "Super Admin" page
   - Create admin accounts for each department (CS, ENG, etc.)
   - Each department admin can only manage their department's students

### For Department Administrators

1. Login via "Admin Login" page
2. Navigate to "Admin Panel"
3. Download the CSV template
4. Fill in student information
5. Upload and import students (they'll automatically be assigned to your department)
6. View and manage your department's students

### For Students

1. Login with Student ID and temporary password
2. Change password on first login
3. Submit weekly logs via "Submit Log" page
4. View submission history in "View Logs"

### For Supervisors

- Receive email when student submits log
- Click "Approve" or "Reject" button in email
- No login required!

## Project Structure

```
project_log/
├── streamlit_app.py          # Main entry point with student login
├── create_super_admin.py     # Setup script for initial super admin
├── pages/
│   ├── 1_📝_Submit_Log.py   # Log submission form (student)
│   ├── 2_📋_View_Logs.py    # View log history (student)
│   ├── 3_🔐_Change_Password.py  # Password management (student)
│   ├── 4_👨‍💼_Admin.py       # Admin panel (department admin/super admin)
│   ├── 5_✅_Verify.py       # Email verification handler
│   ├── 6_🔑_Admin_Login.py  # Admin authentication
│   └── 7_⭐_Super_Admin.py  # Super admin panel (create dept admins)
├── utils/
│   ├── database.py           # MongoDB operations
│   ├── auth.py               # Authentication & password handling
│   └── email_sender.py       # Email functionality
├── .streamlit/
│   └── secrets.toml.example # Secrets configuration template
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Admin Hierarchy

The system supports a two-tier admin structure:

### Super Admin
- **Access**: Full system access across all departments
- **Can**:
  - Create and manage department admins
  - View and manage all students regardless of department
  - Access all admin features
- **Created**: Via `create_super_admin.py` script

### Department Admin
- **Access**: Limited to their assigned department only
- **Can**:
  - Upload and manage students in their department
  - View submissions from their department's students only
  - Cannot create other admins
- **Created**: By super admin via Super Admin page

## How It Works

### Authentication Flow
1. Student enters username/password
2. Password is hashed with bcrypt and compared to database
3. On success, user info stored in Streamlit session state
4. Session persists across page navigation

### Log Submission Flow
1. Student fills out log form
2. System creates log entry in MongoDB with status "pending"
3. Generates unique verification token
4. Sends email to supervisor with approve/reject links
5. Links contain token: `/verify?token=ABC123&action=approved`

### Verification Flow
1. Supervisor clicks link in email
2. Streamlit loads verification page with token from URL
3. System looks up log by token
4. Updates status to "approved" or "rejected"
5. Student sees updated status in dashboard

## Deploying to Streamlit Community Cloud

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository and branch
   - Set main file: `streamlit_app.py`

3. **Configure Secrets**:
   - Click "Advanced settings" before deploying (or go to app settings after)
   - Paste the contents of your `.streamlit/secrets.toml` file into the secrets section
   - Format should be TOML (same as your local file):
   ```toml
   MONGODB_URI = "mongodb+srv://..."
   GMAIL_USER = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "your-app-password"
   APP_URL = "https://your-app-name.streamlit.app"
   SECRET_KEY = "your-secret-key"
   ```

   **Important**: Update `APP_URL` to your deployed app's URL (e.g., `https://your-app-name.streamlit.app`)

4. **Click Deploy!**

Your app will be live at `https://your-app-name.streamlit.app`

## Troubleshooting

### Email Not Sending

1. Check secrets.toml for GMAIL_USER and GMAIL_APP_PASSWORD
2. Verify App Password is 16 characters, no spaces
3. Ensure 2-factor authentication is enabled on Gmail
4. Use Admin → Test Email to diagnose

### MongoDB Connection Failed

1. Check MongoDB URI format in secrets.toml
2. In MongoDB Atlas, add `0.0.0.0/0` to Network Access (for Streamlit Cloud deployment)
3. Verify database user credentials

### Module Not Found

```bash
pip install -r requirements.txt
```

### Secrets Not Found (Local Development)

Make sure you have created `.streamlit/secrets.toml` from the example file:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

## Security Features

- Passwords hashed with bcrypt (never stored in plain text)
- Session-based authentication
- Password strength validation
- Forced password change on first login
- Secure token generation for verification
- Environment variables for sensitive data

## Learning Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **MongoDB Python Driver**: https://pymongo.readthedocs.io
- **bcrypt Documentation**: https://github.com/pyca/bcrypt/

---

**Built with Streamlit and MongoDB**
