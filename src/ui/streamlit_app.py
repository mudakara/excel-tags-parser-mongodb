"""
Main entry point - Redirects to Home page
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Excel Tags Parser & Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Automatically redirect to Home page
st.switch_page("pages/0_🏠_Home.py")
