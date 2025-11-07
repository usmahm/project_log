"""
Email sending utilities for supervisor notifications.

This module handles sending verification emails to supervisors.
"""

import streamlit as st
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.database import update_log_verification_token


def generate_verification_token():
    """
    Generates a secure random token for verification links.

    secrets module: Cryptographically secure random number generator.
    Better than random module for security purposes.

    Returns:
        str: A random 32-character hexadecimal token
    """
    return secrets.token_urlsafe(32)


def send_verification_email(log_id, student_name, student_email, supervisor_email, week_number, log_content):
    """
    Sends a verification email to the supervisor with approve/reject links.

    How it works:
    1. Generate a unique token
    2. Create links with that token
    3. Send email with both links
    4. When supervisor clicks, token identifies which log to update

    Args:
        log_id: ID of the log to verify
        student_name: Name of the student
        student_email: Email of the student
        supervisor_email: Email of the supervisor
        week_number: Week number of the log
        log_content: The actual log content

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Generate verification token
        token = generate_verification_token()

        # Store token in database
        update_log_verification_token(log_id, token)

        # Get app URL from Streamlit secrets
        app_url = st.secrets.get("APP_URL", "http://localhost:8501")

        # Create verification links
        # These will be handled by a special Streamlit page
        approve_link = f"{app_url}/verify?token={token}&action=approved"
        reject_link = f"{app_url}/verify?token={token}&action=rejected"

        # Create email
        subject = f"Log Verification Required - {student_name} (Week {week_number})"

        # HTML email body with styled buttons
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #2c3e50;">Weekly Log Verification</h2>

                <p>Dear Supervisor,</p>

                <p><strong>{student_name}</strong> has submitted their log for <strong>Week {week_number}</strong>.</p>

                <div style="background-color: #f4f4f4; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Log Content:</h3>
                    <p style="white-space: pre-wrap;">{log_content}</p>
                </div>

                <p><strong>Student Email:</strong> {student_email}</p>

                <p>Please verify this log by clicking one of the buttons below:</p>

                <table cellpadding="0" cellspacing="0" border="0" style="margin: 30px 0;">
                    <tr>
                        <td style="padding-right: 10px;">
                            <a href="{approve_link}"
                               style="background-color: #27ae60;
                                      color: white;
                                      padding: 12px 30px;
                                      text-decoration: none;
                                      border-radius: 5px;
                                      display: inline-block;
                                      font-weight: bold;">
                                ✓ Approve Log
                            </a>
                        </td>
                        <td>
                            <a href="{reject_link}"
                               style="background-color: #e74c3c;
                                      color: white;
                                      padding: 12px 30px;
                                      text-decoration: none;
                                      border-radius: 5px;
                                      display: inline-block;
                                      font-weight: bold;">
                                ✗ Reject Log
                            </a>
                        </td>
                    </tr>
                </table>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="color: #7f8c8d; font-size: 12px;">
                    This is an automated email from the Project Logging System.
                    If you received this in error, please ignore it.
                </p>
            </body>
        </html>
        """

        # Plain text version for email clients that don't support HTML
        plain_body = f"""
Weekly Log Verification

Dear Supervisor,

{student_name} has submitted their log for Week {week_number}.

Log Content:
{log_content}

Student Email: {student_email}

Please verify this log by clicking one of the links below:

Approve: {approve_link}
Reject: {reject_link}

---
This is an automated email from the Project Logging System.
        """

        # Create message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = st.secrets["GMAIL_USER"]
        message['To'] = supervisor_email

        # Attach both plain and HTML versions
        part1 = MIMEText(plain_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        message.attach(part1)
        message.attach(part2)

        # Send email via Gmail SMTP
        gmail_user = st.secrets.get("GMAIL_USER")
        gmail_password = st.secrets.get("GMAIL_APP_PASSWORD")

        if not gmail_user or not gmail_password:
            return False, "Email credentials not configured in secrets"

        # Connect to Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(message)

        return True, f"Verification email sent to {supervisor_email}"

    except Exception as e:
        return False, f"Failed to send email: {str(e)}"


def send_test_email(recipient_email):
    """
    Sends a test email to verify email configuration.

    Args:
        recipient_email: Email to send test to

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        subject = "Test Email - Project Logging System"
        body = "This is a test email. Your email configuration is working correctly!"

        message = MIMEText(body)
        message['Subject'] = subject
        message['From'] = st.secrets["GMAIL_USER"]
        message['To'] = recipient_email

        gmail_user = st.secrets.get("GMAIL_USER")
        gmail_password = st.secrets.get("GMAIL_APP_PASSWORD")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(message)

        return True, "Test email sent successfully!"

    except Exception as e:
        return False, f"Failed to send test email: {str(e)}"
