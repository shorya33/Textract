import streamlit as st

# Function to apply theme based on user's choice
def apply_dark_theme(dark_mode=False):
    if dark_mode:
        # Dark theme CSS
        st.markdown("""
            <style>
            body {
                background-color: #31333F;
                color: #FFFFFF;
            }
            .stApp {
                background-color: #31333F;
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        # Light theme CSS (default)
        st.markdown("""
            <style>
            body {
                background-color: #FFFFFF;
                color: #31333F;
            }
            .stApp {
                background-color: #FFFFFF;
            }
            </style>
            """, unsafe_allow_html=True)