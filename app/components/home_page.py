import streamlit as st

def show_page():
    st.title("🏡 나만의 완벽한 동네 찾기")
    st.write("")

    st.markdown(
        """
        ### 집 구하기, 이제 혼자 고민하지 마세요!
        """
    ) 
    st.write("")

    st.markdown(
        """
        ##### 혹시 이런 생각 해보신 적 있나요?
        - *"어디 살지 정말 모르겠어..."*
        - *"내가 원하는 조건에 딱 맞는 곳이 있을까?"*
        - *"발품 팔기엔 너무 피곤하고...* 🙄 *"*
        """
    ) 
    st.write("")

    st.markdown(
        """
        ##### 걱정 마세요! 모든 걸 고려해서 딱! 맞는 동네를 찾아드려요.

        간단한 설문 하나만 답해주시면, 여러분의 라이프스타일과 우선순위를 꼼꼼히 분석해서  
        실시간 데이터와 함께 딱 맞는 동네를 추천해드립니다! 📊
        """
    )
    st.write("")

    st.markdown(    
        """
        ##### ✨ 이런 것들을 다 고려해드려요
        - 🚇 출퇴근 시간과 교통편의성
        - 💰 예산에 맞는 현실적인 옵션
        - 🛒 생활 편의시설 접근성
        - 🏡 주거환경과 동네 분위기
        """
    )
    st.write("")

    if st.button("나만의 완벽한 동네 찾기", use_container_width=True):
        st.session_state.page = "survey"
        st.rerun()