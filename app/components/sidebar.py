import streamlit as st
from utils.state_manager import navigate_to

def render_sidebar():

    st.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .nav-button {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 10px;
            padding: 12px 20px;
            margin: 5px 0;
            width: 100%;
            color: white;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: left;
        }

        .nav-button:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(5px);
        }

        .nav-button.active {
            background: rgba(255, 255, 255, 0.3);
            border-left: 4px solid #fff;
        }

        .sidebar-title {
            color: black;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
        }       
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.markdown('<div class="sidebar-title">📱 메뉴</div>', unsafe_allow_html=True)

        if st.button("🏠 홈", use_container_width=True):
            navigate_to("home")
        if st.button("📋 설문", use_container_width=True):
            navigate_to("survey")
        if st.button("📊 분석", use_container_width=True):
            navigate_to("analysis")
        