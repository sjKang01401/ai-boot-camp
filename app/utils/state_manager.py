import streamlit as st

def get_state(key, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value
    return st.session_state[key]

def set_state(key, value):
    st.session_state[key] = value

def init_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "home"

def navigate_to(page_name):
    # 세션 변경
    st.session_state.page = page_name