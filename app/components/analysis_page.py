import streamlit as st
from utils.feign import start_analysis_workflow, get_survey_by_id
import json
from datetime import datetime

def show_page():
    st.title("📊 동네 분석 결과")
    st.write("""선택된 설문을 기반으로 동네를 분석하고 추천합니다.
    """)

    selected_survey_id = st.session_state.get("selected_survey_id")

    if selected_survey_id:

        # Fetch and display selected survey details
        survey_result = get_survey_by_id(selected_survey_id)
        if survey_result["success"]:
            survey = survey_result["data"]
            if survey:
                with st.container(border=True):
                    created_at_dt = datetime.fromisoformat(survey["created_at"].replace("Z", "+00:00"))
                    formatted_created_at = created_at_dt.strftime("%Y년 %m월 %d일 %H시%M분")
                    
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
            else:
                st.info("선택된 설문 데이터를 찾을 수 없습니다.")
        else:
            st.error(f"설문 데이터를 불러오는 데 실패했습니다: {survey_result['message']}")
        
        if st.button("분석 시작", key="start_analysis_button"):
            with st.spinner("분석이 진행 중입니다... 완료까지 잠시 기다려주세요."):
                                
                workflow_response = start_analysis_workflow(selected_survey_id)

                if workflow_response["success"]:
                    workflow_result = workflow_response["data"]
                    if workflow_result:
                        process_streaming_response(workflow_result)

    else:
        st.info("선택된 설문이 없습니다. 설문 페이지에서 설문을 선택해주세요.")


def _display_analysis_results(agent_type, response, docs):

    st.markdown(f"""#### {AnalysisAgentType.to_korean(agent_type)} 결과""")

    if isinstance(response, list):
        key_to_korean_map = {
            AnalysisAgentType.DATA_COLLECTOR: {
                'distance_to_work_school_location': '직장/학교까지 거리',
                'time_to_work_school_location': '직장/학교까지 시간',
                'distance_to_frequent_location': '자주 가는 곳까지 거리',
                'time_to_frequent_location': '자주 가는 곳까지 시간'
            },
            AnalysisAgentType.REGIONAL_ANALYZER: {
                'analysis_details': '분석 내용',
                'pros': '장점',
                'cons': '단점'
            },
            AnalysisAgentType.BUDGET_OPTIMIZER: {
                'budget_suitability': '예산 적합도',
                'pros': '장점',
                'cons': '단점'
            },
            AnalysisAgentType.RECOMMENDATION_SYNTHESIZER: {
                'score': '종합 점수',
                'detailed_analysis': '종합 분석결과',
                'pros': '장점',
                'cons': '단점',
                'recommendation_reason': '추천 이유',
            },
        }
        current_key_map = key_to_korean_map.get(agent_type, {})

        for i, item in enumerate(response):
            st.markdown(f"##### {i+1}. {item.get('area_name', 'N/A')}")

            markdown_text = ""
            for key, value in item.items():
                if key != 'area_name':
                    korean_key = current_key_map.get(key, key.replace('_', ' ').title())
                    if isinstance(value, list):
                        markdown_text += f"- **{korean_key}**\n"
                        for sub_item in value:
                            markdown_text += f"  - {sub_item}\n"
                    else:
                        markdown_text += f"- **{korean_key}** : {value}\n"

            st.markdown(markdown_text)

            if agent_type == AnalysisAgentType.RECOMMENDATION_SYNTHESIZER:
                if item['area_name'] in docs:
                    with st.expander(f"{item['area_name']} 상세 정보", expanded=False):
                        for doc_item in docs[item['area_name']]:
                            formatted_doc = doc_item.replace('\.', '\.\n')
                            st.markdown(formatted_doc)
    else:
        st.markdown(response)


def process_streaming_response(response):
    for chunk in response.iter_lines():
        if not chunk:
            continue

        # 'data: ' 접두사 제거
        line = chunk.decode("utf-8")

        # line의 형태는 'data: {"type": "update", "data": {}}'
        if not line.startswith("data: "):
            continue

        data_str = line[6:]  # 'data: ' 부분 제거

        try:
            # JSON 데이터 파싱
            event_data = json.loads(data_str)

            # 이벤트 데이터 처리
            is_complete = process_event_data(event_data)

            if is_complete:
                break

        except json.JSONDecodeError as e:
            st.error(f"JSON 파싱 오류: {e}")

class AnalysisAgentType:
    DATA_COLLECTOR = "DATA_COLLECTOR"
    REGIONAL_ANALYZER = "REGIONAL_ANALYZER"
    BUDGET_OPTIMIZER = "BUDGET_OPTIMIZER"
    RECOMMENDATION_SYNTHESIZER = "RECOMMENDATION_SYNTHESIZER"

    @classmethod
    def to_korean(cls, role: str) -> str:
        if role == cls.DATA_COLLECTOR:
            return "후보 지역 수집"
        elif role == cls.REGIONAL_ANALYZER:
            return "지역 분석"
        elif role == cls.BUDGET_OPTIMIZER:
            return "예산 최적화"
        elif role == cls.RECOMMENDATION_SYNTHESIZER:
            return "종합 추천"
        else:
            return role

def process_event_data(event_data):

    # 이벤트 종료
    if event_data.get("type") == "end":
        return True

    # 새로운 메세지
    if event_data.get("type") == "update":
        # state 추출
        data = event_data.get("data", {})

        role = data.get("role")
        response = data["response"]
        docs = data.get("docs", {})

        avatar_map = {
            AnalysisAgentType.DATA_COLLECTOR: "📌",
            AnalysisAgentType.REGIONAL_ANALYZER: "🗺️",
            AnalysisAgentType.BUDGET_OPTIMIZER: "💰",
            AnalysisAgentType.RECOMMENDATION_SYNTHESIZER: "💡",
        }
        avatar = avatar_map.get(role, "📊")

        with st.chat_message(AnalysisAgentType.to_korean(role), avatar=avatar):
            _display_analysis_results(role, response, docs)

    return False