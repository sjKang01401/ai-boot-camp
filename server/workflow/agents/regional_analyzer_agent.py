from workflow.state import AnalysisAgentType
from .analysis_agent import AnalysisAgent
from typing import Dict, Any
import json
from utils.json_encoder import CustomJsonEncoder

class RegionalAnalyzerAgent(AnalysisAgent):
    """각 후보 지역의 생활 편의성 분석"""

    def __init__(self, session_id: str = None):
        super().__init__(
            system_prompt="당신은 지역 분석가입니다. 당신의 임무는 각 후보 지역의 생활 편의성을 분석하는 것입니다. 제공된 후보 지역 목록에 대해 사용자의 설문조사 데이터를 기반으로 교통, 교육, 상업 시설, 자연 환경, 치안 등 다양한 측면에서 상세하게 분석하고, 각 지역의 장단점을 명확하게 제시해야 합니다.",
            role=AnalysisAgentType.REGIONAL_ANALYZER,
            session_id=session_id
        )

    def _handle_response(self, analysis_state: Dict[str, Any]) -> str:
        response_content = analysis_state.get('response', '')

        print(response_content)

        if response_content.startswith('```json\n'):
            json_string = response_content[len('```json\n'):]
        elif response_content.startswith('json\n'):
            json_string = response_content[len('json\n'):]
        else:
            json_string = response_content

        if json_string.endswith('\n```'):
            json_string = json_string[:-len('\n```')]

        try:
            parsed_json = json.loads(json_string)
            regional_analysis_results = parsed_json.get('regional_analysis_results', [])

            analysis_state['analysis_result'][self.role] = regional_analysis_results
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            analysis_state['response'] = f"데이터 수집 중 오류가 발생했습니다: {e}"
            analysis_state['analysis_result'][self.role] = {}

        return analysis_state

    def _create_prompt(self, analysis_state: Dict[str, Any]) -> str:

        survey_data = analysis_state['survey_data']
        data_collector_result = analysis_state['analysis_result'].get(AnalysisAgentType.DATA_COLLECTOR, {})

        return f"""다음은 사용자의 설문조사 데이터와 후보 지역 수집 에이전트의 결과입니다.

        설문조사 데이터:
        {json.dumps(survey_data, ensure_ascii=False, indent=2, cls=CustomJsonEncoder)}

        후보 지역 수집 결과 (DATA_COLLECTOR):
        {json.dumps(data_collector_result, ensure_ascii=False, indent=2, cls=CustomJsonEncoder)}

        위 데이터를 바탕으로 각 후보 지역에 대해 다음 지시에 따라 상세하게 지역 분석을 수행하고, 그 결과를 JSON 형식으로 반환해 주세요.

        요청 작업:
        1. 각 후보 지역에 대해 사용자의 설문조사 데이터를 기반으로 교통, 교육, 상업 시설, 자연 환경, 치안 등 다양한 측면에서 상세하게 분석해 주세요.
        2. 각 지역의 주요 장점과 단점을 명확하게 제시해 주세요.

        답변은 아래의 JSON 형식에 맞추어 반환해주세요.

        JSON 출력 형식 예시:
        {{
          "regional_analysis_results": [
            {{
              "area_name": "string (지역 이름)",
              "analysis_details": "string (해당 지역에 대한 상세 분석 내용)",
              "pros": [
                "string (장점 1)",
                "string (장점 2)"
              ],
              "cons": [
                "string (단점 1)",
                "string (단점 2)"
              ]
            }}
          ]
        }}
        """
