import streamlit as st
import requests
from urllib.parse import urlencode
import os

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-client-id-here")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-client-secret-here")
REDIRECT_URI = "http://localhost:8501"

def generate_auth_url():
    """Generate Google OAuth authorization URL"""
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid profile email',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

def get_access_token(auth_code):
    """Exchange authorization code for access token"""
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()
    return None

def get_user_info(access_token):
    """Get user info from Google using access token"""
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(userinfo_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def init_session_state():
    """Initialize session state variables"""
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_picture' not in st.session_state:
        st.session_state.user_picture = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = 'employee'
    if 'is_guest' not in st.session_state:
        st.session_state.is_guest = False
    if 'is_logged_in' not in st.session_state:
        st.session_state.is_logged_in = False

def login_as_guest():
    """Set session state for guest login"""
    st.session_state.is_guest = True
    st.session_state.is_logged_in = True
    st.session_state.user_email = "guest@interview.local"
    st.session_state.user_name = "Guest User"
    st.session_state.user_picture = None
    st.session_state.user_role = 'employee'

def login_with_google(email, name, picture, role='employee'):
    """Set session state for Google login"""
    st.session_state.is_guest = False
    st.session_state.is_logged_in = True
    st.session_state.user_email = email.lower().strip()  # Normalize email to lowercase
    st.session_state.user_name = name
    st.session_state.user_picture = picture
    st.session_state.user_role = role

def logout():
    """Clear session state"""
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.user_picture = None
    st.session_state.is_guest = False
    st.session_state.is_logged_in = False
    st.session_state.user_role = 'employee'

def is_user_logged_in():
    """Check if user is logged in"""
    return st.session_state.get('is_logged_in', False)

def get_current_user():
    """Get current logged-in user info"""
    return {
        'email': st.session_state.get('user_email'),
        'name': st.session_state.get('user_name'),
        'picture': st.session_state.get('user_picture'),
        'is_guest': st.session_state.get('is_guest', False),
        'role': st.session_state.get('user_role', 'employee')
    }
