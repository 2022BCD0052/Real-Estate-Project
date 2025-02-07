import streamlit as st

st.set_page_config(page_title="My Streamlit App", page_icon="\U0001f4cc", layout="wide")

# Custom CSS for white background
st.markdown(
    """
    <style>
        .stApp {
            background-color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("\U0001f3e0 Welcome to My Streamlit App")
st.write("Use the sidebar to navigate through different pages.")
