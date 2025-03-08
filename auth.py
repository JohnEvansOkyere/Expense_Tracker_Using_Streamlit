import streamlit as st
from db_config import create_user, get_user_by_email, get_user_by_username
import re

def init_session_state():
    """Initialize session state variables"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

def login_page():
    """Handle user login"""
    st.title("Login to Expense Tracker")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
                return
                
            if not validate_email(email):
                st.error("Invalid email format")
                return
            
            user = get_user_by_email(email)
            if user and user.verify_password(password):
                st.session_state.user = user
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.rerun()  # Refresh the app to show the main interface
            else:
                st.error("Invalid email or password")
    
    st.markdown("---")
    st.write("Don't have an account?")
    if st.button("Sign Up"):
        st.session_state.show_signup = True
        st.rerun()  # Refresh the app to show the signup page

def signup_page():
    """Handle user registration"""
    st.title("Create an Account")
    
    with st.form("signup_form"):
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not all([email, username, password, confirm_password]):
                st.error("Please fill in all fields")
                return
            
            if not validate_email(email):
                st.error("Invalid email format")
                return
            
            if len(username) < 3:
                st.error("Username must be at least 3 characters long")
                return
            
            is_valid_password, password_message = validate_password(password)
            if not is_valid_password:
                st.error(password_message)
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if get_user_by_email(email):
                st.error("Email already registered")
                return
                
            if get_user_by_username(username):
                st.error("Username already taken")
                return
            
            try:
                user = create_user(email, username, password)
                if user:
                    st.success("Account created successfully! Please log in.")
                    st.session_state.show_signup = False
                    st.rerun()  # Refresh the app to show the login page
                else:
                    st.error("Error creating account. Please try again.")
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")
    
    st.markdown("---")
    st.write("Already have an account?")
    if st.button("Login"):
        st.session_state.show_signup = False
        st.rerun()  # Refresh the app to show the login page

def logout():
    """Handle user logout"""
    for key in ['user', 'authenticated', 'show_signup']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()  # Refresh the app to return to the login page

# Initialize session state
init_session_state()

# Main App Logic
if not st.session_state.authenticated:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
else:
    # Display the main interface (replace this with your main app logic)
    st.title(f"Welcome, {st.session_state.user.username}!")
    st.write("You are logged in.")
    if st.button("Logout"):
        logout()