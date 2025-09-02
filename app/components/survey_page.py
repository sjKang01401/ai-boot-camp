import streamlit as st
from datetime import datetime
from utils.feign import get_recent_surveys, save_survey

def show_page():
    st.title("🎯 나만의 완벽한 동네 찾기 설문")
    st.write("")

    st.markdown(
        """
        #### 이제 본격적으로 여러분에 대해 알려주세요! 😊
        """
    ) 
    st.write("")

    st.markdown(
        """
        어떤 동네가 딱 맞을지 알아보려면, 여러분이 어떤 분이고 뭘 중요하게 생각하는지 알아야 해요.  
        **너무 깊게 고민하지 마시고** 편하게 답해주세요! 정답은 없으니까 지금 드는 생각 그대로만 선택하시면 돼요. 🤗

        > 💡 **Tip**: 솔직하게 답할수록 더 정확한 추천을 받을 수 있어요!  
        > "이래야 할 것 같은데..."보다는 "나는 진짜 이런 게 좋아!"가 중요해요. ✨
        """
    ) 
    
    st.write("")

    with st.expander("최근 설문 기준으로 동네찾기"):
        render_recent_surveys()

    st.markdown("---")
    st.write("")

    render_create_survey()

def _go_to_analysis_with_survey_id(survey_id):
    st.session_state.page = "analysis"
    st.session_state.selected_survey_id = survey_id

def render_recent_surveys():
    
    # 최근 설문 기록 가져오기
    recent_surveys_result = get_recent_surveys()
    
    if recent_surveys_result["success"]:
        recent_surveys = recent_surveys_result["data"]
        if recent_surveys:
            cols = st.columns(3)
            for i, survey in enumerate(recent_surveys):
                with cols[i]:

                    created_at_dt = datetime.fromisoformat(survey["created_at"].replace("Z", "+00:00"))
                    formatted_created_at = created_at_dt.strftime("%Y년 %m월 %d일 %H시%M분")
                    
                    with st.container(border=True):
                        st.markdown(f"#### {formatted_created_at} 설문 결과")
                        st.write(f"**가족 구성:** {survey.get('family_type', 'N/A')}")
                        if survey.get('family_type_etc'):
                            st.write(f"  - 기타: {survey['family_type_etc']}")
                        st.write(f"**연령대:** {survey.get('age_group', 'N/A')}")
                        st.write(f"**주로 하시는 일:** {survey.get('job_type', 'N/A')}")
                        if survey.get('job_type_etc'):
                            st.write(f"  - 기타: {survey['job_type_etc']}")
                        st.write(f"**주거 형태:** {survey.get('housing_type', 'N/A')}")
                        if survey.get('housing_type') == '전세로 안정적으로':
                            st.write(f"**전세 예산:** {survey.get('jeonse_budget', 'N/A')}")
                        elif survey.get('housing_type') == '매매로 내 집 마련':
                            st.write(f"**매매 예산:** {survey.get('maemae_budget', 'N/A')}")
                        st.write(f"**월 주거비 부담:** {survey.get('monthly_cost', 'N/A')}")
                        st.write(f"**직장/학교:** {survey.get('work_school_location', 'N/A')}")
                        st.write(f"**자주 가는 곳:** {survey.get('frequent_location', 'N/A')}")
                        st.write(f"**기타 목적지:** {survey.get('other_location', 'N/A')}")
                        st.write(f"**교통수단:** {survey.get('transport_method', 'N/A')}")
                        st.write(f"**출퇴근 시간:** {survey.get('commute_time', 'N/A')}")
                        st.write(f"**중요도 1순위:** {survey.get('first_priority', 'N/A')}")
                        st.write(f"**중요도 2순위:** {survey.get('second_priority', 'N/A')}")
                        st.write(f"**중요도 3순위:** {survey.get('third_priority', 'N/A')}")
                        st.write(f"**집에서 주로 하는 일:** {survey.get('home_activity', 'N/A')}")
                        st.write(f"**주말에 주로 하는 일:** {survey.get('weekend_activity', 'N/A')}")
                        st.write(f"**소음 민감도:** {survey.get('noise_sensitivity', 'N/A')}")
                        st.write(f"**꼭 피하고 싶은 것:** {survey.get('avoid_item', 'N/A')}")
                        if survey.get('avoid_item_etc'):
                            st.write(f"  - 기타: {survey['avoid_item_etc']}")
                        st.write(f"**꼭 있었으면 하는 것:** {survey.get('want_item', 'N/A')}")
                        if survey.get('want_item_etc'):
                            st.write(f"  - 기타: {survey['want_item_etc']}")
                        st.write(f"**추가 의견:** {survey.get('additional_comments', 'N/A')}")

                        st.button("동네 추천받기", key=f"find_neighborhood_{survey['id']}", use_container_width=True, on_click=_go_to_analysis_with_survey_id, args=(survey['id'],))

        else:
            st.info("아직 저장된 설문 데이터가 없습니다.")
    else:
        st.error(recent_surveys_result["message"])

def render_create_survey():

    # 설문
    st.markdown("### 👨‍👩‍👧‍👦 먼저, 어떤 분이신지 알려주세요!")

    st.write("#### 현재 가족 구성은 어떻게 되세요?")
    family_options = ["나 혼자 살림 (1인 가구)", "연인/부부 둘이서 (신혼/커플)", "아이와 함께 (육아 가정)", "부모님과 함께 (3세대)", "기타"]
    family_type = st.radio("family_type", family_options, key="family_type", horizontal=True, label_visibility="collapsed")
    if family_type == "기타":
        st.text_input("기타 가족 구성", key="family_type_etc")

    st.write("#### 연령대를 알려주세요")
    age_options = ["20대 (자유롭게 살고 싶어요)", "30대 (안정적으로 정착하고 싶어요)", "40대 (가족 중심으로 생각해요)", "50대 이상 (편리함이 최고예요)"]
    st.radio("age_group", age_options, key="age_group", horizontal=True, label_visibility="collapsed")

    st.write("#### 주로 하시는 일은?")
    job_options = ["회사원 (정해진 출퇴근)", "프리랜서/재택근무 (시간 자유로움)", "자영업 (내 사업 있음)", "학생 (캠퍼스 라이프)", "기타"]
    job_type = st.radio("job_type", job_options, key="job_type", horizontal=True, label_visibility="collapsed")
    if job_type == "기타":
        st.text_input("기타 직업", key="job_type_etc")

    st.markdown("---")
    st.markdown("### 💰 현실적인 이야기, 예산은 어느 정도 생각하고 계세요?")

    st.write("#### 주거 형태는?")
    housing_options = ["전세로 안정적으로", "매매로 내 집 마련", "월세로 부담 없이", "아직 고민 중"]
    housing_type = st.radio("housing_type", housing_options, key="housing_type", horizontal=True, label_visibility="collapsed")

    if housing_type == "전세로 안정적으로":
        st.write("#### 전세 예산 범위는?")
        jeonse_budget_options = ["3억 미만 (알뜰하게)", "3억~5억 (적당히)", "5억~7억 (여유롭게)", "7억 이상 (넉넉하게)"]
        st.radio("jeonse_budget", jeonse_budget_options, key="jeonse_budget", horizontal=True, label_visibility="collapsed")
    elif housing_type == "매매로 내 집 마련":
        st.write("#### 매매 예산 범위는?")
        maemae_budget_options = ["5억 미만", "5억~10억", "10억~15억", "15억 이상"]
        st.radio("maemae_budget", maemae_budget_options, key="maemae_budget", horizontal=True, label_visibility="collapsed")

    st.write("#### 월 주거비 부담은 어느 정도까지?")
    monthly_cost_options = ["100만원 미만", "100~200만원", "200~300만원", "300만원 이상 괜찮아요"]
    st.radio("monthly_cost", monthly_cost_options, key="monthly_cost", horizontal=True, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 🚇 매일매일 이동하는 곳들을 알려주세요!")

    st.write("#### 주요 목적지를 입력해주세요")
    st.text_input("1. 직장/학교: (예: 강남역/역삼동)", key="work_school_location")
    st.text_input("2. 자주 가는 곳: (예: 친정, 병원, 헬스장 등)", key="frequent_location")
    st.text_input("3. 기타:", key="other_location")

    st.write("#### 교통수단은 주로?")
    transport_options = ["지하철이 최고! (🚇)", "버스도 괜찮아요 (🚌)", "내 차가 있어요 (🚗)", "걸어다니는 걸 좋아해요 (🚶‍♂️)", "자전거/킥보드 애용 (🚴‍♂️)"]
    st.radio("transport_method", transport_options, key="transport_method", horizontal=True, label_visibility="collapsed")

    st.write("#### 출퇴근 시간은 얼마까지 OK?")
    commute_time_options = ["30분 이내 (시간이 금!)", "30분~1시간 (적당해요)", "1시간~1시간 30분 (참을 만해요)", "시간보다 다른 게 더 중요해요"]
    st.radio("commute_time", commute_time_options, key="commute_time", horizontal=True, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 🏠 살면서 가장 중요하게 생각하는 건 뭔가요?")
    st.markdown("> **가장 중요하다고 생각하는 요소 3가지를 순서대로 선택해주세요.**")
    importance_options = [
        "🏫 교육 환경 (좋은 학군, 학원가 접근성)",
        "🏥 의료 시설 (병원, 약국 가까이)",
        "🛒 쇼핑 편의 (마트, 시장 가까이)",
        "🎭 문화생활 (영화관, 도서관, 헬스장)",
        "🌳 자연환경 (공원, 산책로, 깨끗한 공기)",
        "🔒 치안/안전 (밤에도 안전하게)",
        "🍽️ 먹거리 (맛집, 카페 많은 곳)",
        "🚗 주차 (주차 걱정 없이)"
    ]

    # 1순위 선택
    first_priority = st.selectbox("1순위", ["선택하세요"] + importance_options, key="first_priority", label_visibility="collapsed")

    # 2순위 선택 (1순위에서 선택된 항목 제외)
    second_options = [opt for opt in importance_options if opt != first_priority]
    second_priority = st.selectbox("2순위", ["선택하세요"] + second_options, key="second_priority", label_visibility="collapsed")

    # 3순위 선택 (1, 2순위에서 선택된 항목 제외)
    third_options = [opt for opt in second_options if opt != second_priority]
    third_priority = st.selectbox("3순위", ["선택하세요"] + third_options, key="third_priority", label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 🎨 라이프스타일을 더 자세히 알려주세요!")

    st.write("#### 집에서 주로 뭘 하시나요?")
    home_activity_options = ["넷플릭스 정주행 (조용한 곳 선호)", "요리해서 먹기 (마트 접근성 중요)", "운동/헬스 (체육시설 근처)", "친구들과 만나기 (번화가 선호)", "반려동물과 시간 (산책로 중요)"]
    st.radio("home_activity", home_activity_options, key="home_activity", horizontal=True, label_visibility="collapsed")

    st.write("#### 주말엔 주로?")
    weekend_activity_options = ["집에서 쉬기 (주거환경 중요)", "카페/맛집 탐방 (상권 발달지역)", "운동/야외활동 (공원/체육시설 근처)", "쇼핑/영화 (대형몰 접근성)", "친구/가족 만나기 (교통 편의성)"]
    st.radio("weekend_activity", weekend_activity_options, key="weekend_activity", horizontal=True, label_visibility="collapsed")

    st.write("#### 소음에 대한 민감도는?")
    noise_sensitivity_options = ["조용한 게 최고 (주택가 선호)", "적당한 소음은 괜찮아요", "활기찬 분위기 좋아해요 (상가 근처 OK)"]
    st.radio("noise_sensitivity", noise_sensitivity_options, key="noise_sensitivity", horizontal=True, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 🌟 마지막으로, 특별히 원하는 게 있다면?")

    st.write("#### 꼭 피하고 싶은 것")
    avoid_options = ["언덕 많은 곳", "대학가 (시끄러운 곳)", "공장 근처", "고층 아파트", "기타"]
    avoid_item = st.radio("avoid_item", avoid_options, key="avoid_item", horizontal=True, label_visibility="collapsed")
    if avoid_item == "기타":
        st.text_input("기타 피하고 싶은 것", key="avoid_item_etc")

    st.write("#### 꼭 있었으면 하는 것")
    want_options = ["놀이터/키즈카페 (아이 있음)", "24시간 편의점", "배달 잘 되는 곳", "주차장 넉넉한 곳", "기타"]
    want_item = st.radio("want_item", want_options, key="want_item", horizontal=True, label_visibility="collapsed")
    if want_item == "기타":
        st.text_input("기타 꼭 있었으면 하는 것", key="want_item_etc")

    st.write("#### 하고 싶은 말이 있다면?")
    st.text_area("자유롭게 적어주세요!", key="additional_comments")

    st.button("내 취향에 맞는 동네 추천받기", key="submit_survey", use_container_width=True)

    if st.session_state.get("submit_survey"):
        survey_data = {
            "family_type": st.session_state.get("family_type"),
            "family_type_etc": st.session_state.get("family_type_etc", ""),
            "age_group": st.session_state.get("age_group"),
            "job_type": st.session_state.get("job_type"),
            "job_type_etc": st.session_state.get("job_type_etc", ""),
            "housing_type": st.session_state.get("housing_type"),
            "jeonse_budget": st.session_state.get("jeonse_budget", ""),
            "maemae_budget": st.session_state.get("maemae_budget", ""),
            "monthly_cost": st.session_state.get("monthly_cost"),
            "work_school_location": st.session_state.get("work_school_location"),
            "frequent_location": st.session_state.get("frequent_location"),
            "other_location": st.session_state.get("other_location"),
            "transport_method": st.session_state.get("transport_method"),
            "commute_time": st.session_state.get("commute_time"),
            "first_priority": st.session_state.get("first_priority"),
            "second_priority": st.session_state.get("second_priority"),
            "third_priority": st.session_state.get("third_priority"),
            "home_activity": st.session_state.get("home_activity"),
            "weekend_activity": st.session_state.get("weekend_activity"),
            "noise_sensitivity": st.session_state.get("noise_sensitivity"),
            "avoid_item": st.session_state.get("avoid_item"),
            "avoid_item_etc": st.session_state.get("avoid_item_etc", ""),
            "want_item": st.session_state.get("want_item"),
            "want_item_etc": st.session_state.get("want_item_etc", ""),
            "additional_comments": st.session_state.get("additional_comments", "")
        }

        result = save_survey(survey_data)
        if result["success"]:
            st.success(result["message"])
            # st.json(result["data"])
        else:
            st.error(result["message"])