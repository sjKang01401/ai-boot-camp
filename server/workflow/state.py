# LangGraph 상태 정의 - RAG 관련 필드 추가
from typing import Any, Dict, TypedDict


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


class AnalysisState(TypedDict):
    survey_data: Dict[str, Any] # 사용자의 입력 설문 데이터
    role: str # Agent 역할
    response: str # LLM 응답
    docs: Dict[str, Any]  # RAG 결과
    analysis_result: Dict[str, Any] # 각 에이전트의 분석 결과    