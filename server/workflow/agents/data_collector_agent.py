from workflow.state import AnalysisAgentType
from .analysis_agent import AnalysisAgent
import json
from typing import Dict, Any

class DataCollectorAgent(AnalysisAgent):
    """후보 지역 수집 담당"""

    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt="당신은 데이터 수집가입니다. 당신의 역할은 설문조사를 기반으로 관련 지역 데이터를 수집하는 것입니다.",
            role=AnalysisAgentType.DATA_COLLECTOR,
            k=k,
            session_id=session_id
        )
    
    def _handle_response(self, analysis_state: Dict[str, Any]) -> str:

      response_content = analysis_state.get('response', '')

      # Remove leading '```json\n' or 'json\n'
      if response_content.startswith('```json\n'):
          json_string = response_content[len('```json\n'):]
      elif response_content.startswith('json\n'):
          json_string = response_content[len('json\n'):]
      else:
          json_string = response_content

      # Remove trailing '\n```'
      if json_string.endswith('\n```'):
          json_string = json_string[:-len('\n```')]

      try:
          parsed_json = json.loads(json_string)
          recommended_areas = parsed_json.get('recommended_areas', [])

          analysis_state['analysis_result'][self.role] = recommended_areas

      except json.JSONDecodeError as e:
          print(f"JSON 파싱 오류: {e}")
          analysis_state['analysis_result'][self.role] = []

      return analysis_state

    def _create_prompt(self, analysis_state: Dict[str, Any]) -> str:
        
        survey_data = analysis_state['survey_data']

        return f"""다음 설문조사 데이터를 바탕으로 거주하기 좋은 주변 지역을 추천해 주세요.

        설문조사 데이터:
        - 주요 위치(직장/학교): {survey_data.get('work_school_location', 'N/A')}
        - 희망 통근 시간: {survey_data.get('commute_time', 'N/A')}
        - 주요 이동 수단: {survey_data.get('transport_method', 'N/A')}
        - 자주 가는 장소: {survey_data.get('frequent_location', 'N/A')}

        요청 작업:
        1. '주요 위치'를 중심으로 '희망 통근 시간'과 '주요 이동 수단'을 고려하여 이동 가능한 반경을 계산해 주세요.
        2. 계산된 반경 내에서 거주할 만한 지역들을 여러 개 추천해 주세요.
        3. 추천된 각 지역에서 '주요 위치'와 '자주 가는 장소'까지의 거리와 예상 소요 시간을 분석해 주세요.
        4. 분석 결과를 바탕으로 최종 추천 지역 목록을 나열해주세요.

        답변은 아래의 JSON 형식에 맞추어 반환해주고, 그외의 내용은 답변에 넣지마세요.

        JSON 출력 형식 예시:
        {{
          "recommended_areas": [
            {{
              "area_name": "string (추천 지역의 이름)",
              "distance_to_work_school_location": "string (주요 위치까지의 거리, 예: '10km')",
              "time_to_work_school_location": "string (주요 위치까지의 예상 소요 시간, 예: '20분')",
              "distance_to_frequent_location": "string (자주 가는 장소까지의 거리, 예: '10km')",
              "time_to_frequent_location": "string (자주 가는 장소까지의 예상 소요 시간, 예: '20분')"
            }},
            {{
              "area_name": "string (다른 추천 지역의 이름)",
              "distance_to_work_school_location": "string (다른 주요 위치까지의 거리, 예: '8km')",
              "time_to_work_school_location": "string (다른 주요 위치까지의 예상 소요 시간, 예: '15분')",
              "distance_to_frequent_location": "string (다른 자주 가는 장소까지의 거리, 예: '5km')",
              "time_to_frequent_location": "string (다른 자주 가는 장소까지의 예상 소요 시간, 예: '10분')"
            }}
          ]
        }}
        """