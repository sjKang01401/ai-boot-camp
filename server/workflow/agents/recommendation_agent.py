from workflow.state import AnalysisAgentType
from .analysis_agent import AnalysisAgent
from typing import Dict, Any
import json
from utils.json_encoder import CustomJsonEncoder

class RecommendationAgent(AnalysisAgent):
    """최종 추천 담당"""

    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt="당신은 모든 분석 결과를 종합하여 사용자에게 최적의 동네를 추천하는 전문가입니다. 지역 분석, 예산 분석, 후보 지역 데이터를 바탕으로 가장 적합한 TOP 3 지역을 선정하고, 각 지역의 상세 분석, 장단점, 추천 이유를 명확하게 설명해야 합니다.",
            role=AnalysisAgentType.RECOMMENDATION_SYNTHESIZER,
            k=k,
            session_id=session_id
        )
    
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
            top_3_recommendations = parsed_json.get('top_3_recommendations', [])

            analysis_state['analysis_result'][self.role] = top_3_recommendations
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            analysis_state['response'] = f"데이터 수집 중 오류가 발생했습니다: {e}"
            analysis_state['analysis_result'] = {}

        return analysis_state

    def _create_prompt(self, analysis_state: Dict[str, Any]) -> str:
        survey_data = analysis_state['survey_data']
        data_collector_result = analysis_state['analysis_result'].get('DATA_COLLECTOR', {})
        regional_analyzer_result = analysis_state['analysis_result'].get('REGIONAL_ANALYZER', {})
        budget_optimizer_result = analysis_state['analysis_result'].get('BUDGET_OPTIMIZER', {})

        return f"""다음은 사용자의 설문조사 데이터와 각 에이전트의 분석 결과입니다.

        설문조사 데이터:
        {json.dumps(survey_data, ensure_ascii=False, indent=2, cls=CustomJsonEncoder)}

        후보 지역 수집 결과 (DATA_COLLECTOR):
        {json.dumps(data_collector_result, ensure_ascii=False, indent=2, cls=CustomJsonEncoder)}

        지역 분석 결과 (REGIONAL_ANALYZER):
        {json.dumps(regional_analyzer_result, ensure_ascii=False, indent=2, cls=CustomJsonEncoder)}

        예산 최적화 결과 (BUDGET_OPTIMIZER):
        {json.dumps(budget_optimizer_result, ensure_ascii=False, indent=2, cls=CustomJsonEncoder)}

        위 데이터를 종합하여 다음 지시에 따라 최종 추천 결과를 JSON 형식으로 반환해 주세요.

        요청 작업:
        1. 후보 지역 수집 결과의 각 지역에 대해 지역 분석 결과와 예산 최적화 결과를 바탕으로 점수를 매겨주세요.
        2. 점수를 기준으로 TOP 3 지역을 선정해 주세요.
        3. 선정된 TOP 3 각 지역에 대해 상세 분석을 제공해 주세요.
        4. 각 지역별 장단점과 추천 이유를 명확하게 설명해 주세요.

        답변은 아래의 JSON 형식에 맞추어 반환해주고, 원문 그대로 markdown에 사용될 예정이기 때문에 Escape 처리가 필요한 문자에 대해서는 \를 사용해 Escape 처리 해주세요.

        JSON 출력 형식 예시:
        {{
          "top_3_recommendations": [
            {{
              "area_name": "string (지역 이름)",
              "score": "number (종합 점수)",
              "detailed_analysis": "string (해당 지역에 대한 상세 분석)",
              "pros": [
                "string (장점 1)",
                "string (장점 2)"
              ],
              "cons": [
                "string (단점 1)",
                "string (단점 2)"
              ],
              "recommendation_reason": "string (이 지역을 추천하는 이유)"
            }}
          ]
        }}
        """