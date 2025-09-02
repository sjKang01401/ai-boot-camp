from workflow.state import AnalysisAgentType
from .analysis_agent import AnalysisAgent
from typing import Dict, Any
import json
from utils.json_encoder import CustomJsonEncoder

class BudgetOptimizerAgent(AnalysisAgent):
    """예산 효율성 분석"""

    def __init__(self, session_id: str = None):
        super().__init__(
            system_prompt="당신은 예산 최적화 전문가입니다. 당신의 임무는 사용자의 예산 제약 조건과 주거 형태(전세, 매매, 월세)를 고려하여 각 후보 지역의 예산 적합성을 분석하는 것입니다. 제공된 후보 지역 목록에 대해 사용자의 설문조사 데이터를 기반으로 예산 효율성을 평가하고, 각 지역의 예산 관련 장단점을 명확하게 제시해야 합니다.",
            role=AnalysisAgentType.BUDGET_OPTIMIZER,
            session_id=session_id
        )

    def _create_rag_query(self, analysis_state: Dict[str, Any], area_name: str) -> str:
        return ""

    def _handle_response(self, analysis_state: Dict[str, Any]) -> str:
        response_content = analysis_state.get('response', '')

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
            budget_analysis_results = parsed_json.get('budget_analysis_results', [])

            analysis_state['analysis_result'][self.role] = budget_analysis_results
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

        위 데이터와 제공된 RAG 데이터를 바탕으로 각 후보 지역에 대해 다음 지시에 따라 예산 적합성을 분석하고, 그 결과를 JSON 형식으로 반환해 주세요.

        요청 작업:
        1. 각 후보 지역에 대해 사용자의 예산 제약 조건과 주거 형태(전세, 매매, 월세)를 고려하여 예산 적합성을 평가해 주세요.
        2. 각 지역의 예산 관련 장점과 단점을 명확하게 제시해 주세요.

        다음은 분석에 참고할 RAG 데이터입니다:
        {analysis_state.get("context", "제공된 데이터 없음")}

        답변은 아래의 JSON 형식에 맞추어 반환해주고, 원문 그대로 markdown에 사용될 예정이기 때문에 Escape 처리가 필요한 문자에 대해서는 \를 사용해 Escape 처리 해주세요.

        JSON 출력 형식 예시:
        {{
          "budget_analysis_results": [
            {{
              "area_name": "string (지역 이름)",
              "budget_suitability": "string (예산 적합성 평가, 예: '매우 적합', '적합', '보통', '부적합')",
              "pros": [
                "string (예산 관련 장점 1)",
                "string (예산 관련 장점 2)"
              ],
              "cons": [
                "string (예산 관련 단점 1)",
                "string (예산 관련 단점 2)"
              ]
            }}
          ]
        }}
        """
    
