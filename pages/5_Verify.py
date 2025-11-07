"""
Verification Handler Page

This page processes verification links clicked by supervisors in emails.
URL format: /verify?token=TOKEN&action=approved or rejected
"""

import streamlit as st
from utils.database import verify_log

st.set_page_config(
    page_title="Log Verification",
    page_icon="✅",
    layout="centered"
)

# Get query parameters from URL
# In Streamlit, use st.query_params to access URL parameters
query_params = st.query_params

token = query_params.get("token", None)
action = query_params.get("action", None)

st.title("✅ Log Verification")
st.markdown("---")

if not token or not action:
    st.error("""
    ❌ **Invalid Verification Link**

    This page requires a valid verification token and action.

    If you clicked a link from an email, please make sure you copied the complete URL.
    """)
    st.info("This page is for supervisor verification only. Students should use the main login page.")

elif action not in ['approved', 'rejected']:
    st.error("❌ Invalid action. Must be 'approved' or 'rejected'.")

else:
    # Process the verification
    log = verify_log(token, action)

    if log is None:
        st.error("""
        ❌ **Verification Failed**

        This verification link is either:
        - Invalid
        - Expired
        - Already used

        If you need to re-verify this log, please contact the student or system administrator.
        """)
    else:
        # Success!
        if action == 'approved':
            st.success(f"""
            ✅ **Log Approved Successfully!**

            You have approved the log submission for:

            **Student**: {log['student_name']}
            **Email**: {log['student_email']}
            **Week**: {log['week_number']}
            **Submitted**: {log['submitted_at'].strftime('%Y-%m-%d %H:%M')}

            The student will be able to see this approval status in their dashboard.
            """)
            st.balloons()

            # Show log content for reference
            with st.expander("View Log Content"):
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px; white-space: pre-wrap;">
{log['content']}
                </div>
                """, unsafe_allow_html=True)

        else:  # rejected
            st.warning(f"""
            ❌ **Log Rejected**

            You have rejected the log submission for:

            **Student**: {log['student_name']}
            **Email**: {log['student_email']}
            **Week**: {log['week_number']}
            **Submitted**: {log['submitted_at'].strftime('%Y-%m-%d %H:%M')}

            **Next Steps:**
            Please contact the student ({log['student_email']}) to provide feedback
            on what needs to be improved in their log submission.
            """)

            # Show log content for reference
            with st.expander("View Log Content"):
                st.markdown(f"""
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; white-space: pre-wrap;">
{log['content']}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.info("You can safely close this window now.")
