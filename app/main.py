import json
import os
from dotenv import load_dotenv
import requests
import streamlit as st
from datetime import datetime
from utils.state_manager import init_session_state
from components.sidebar import render_sidebar
from components import home_page, survey_page, analysis_page
from utils.state_manager import navigate_to

st.set_page_config(
        page_title="주거 취향기반 동네 추천", 
        page_icon="🏡", 
        layout="wide",
    )

def render_ui():
    if st.session_state.page == "home":
        home_page.show_page()
    elif st.session_state.page == "survey":
        survey_page.show_page()
    elif st.session_state.page == "analysis":
        analysis_page.show_page()        


if __name__ == "__main__":

    load_dotenv()

    # 세션 상태 초기화
    init_session_state()

    render_sidebar()
    render_ui()
