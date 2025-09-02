from abc import ABC, abstractmethod
import json
from typing import Any, Dict, List, TypedDict
import requests
import os
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langfuse.callback import CallbackHandler
from retrieval.vector_store import search_topic, search_csv
from utils.config import get_llm
from workflow.state import AnalysisState, AnalysisAgentType

load_dotenv()


# 에이전트 내부 상태 타입 정의
class AnalysisAgentState(TypedDict):
    survey_data: Dict[str, Any] # 사용자의 입력 설문 데이터
    
    # role: str # Agent 역할
    message: str # LLM 전달 메시지
    response: str # LLM 응답

    context: Dict[str, Any] # RAG 검색 컨텍스트
    docs: Dict[str, Any]  # RAG 결과  

    analysis_result: Dict[str, Any] # 각 에이전트의 분석 결과    


# 분석 에이전트 추상 클래스 정의
class AnalysisAgent(ABC):

    def __init__(self, system_prompt: str, role: str, k: int = 2, session_id: str = None):
        self.system_prompt = system_prompt
        self.role = role
        self.k = k  # 검색할 문서 개수
        self._setup_graph() # 그래프 설정
        self.session_id = session_id # langfuse 세션 ID

    def _setup_graph(self):
        # 그래프 생성
        workflow = StateGraph(AnalysisAgentState)

        # 노드 추가
        workflow.add_node("retrieve_context", self._retrieve_context) # 자료 검색
        workflow.add_node("prepare_messages", self._prepare_messages) # 메시지 준비
        workflow.add_node("generate_response", self._generate_response) # 응답 생성
        workflow.add_node("update_state", self._update_state) # 상태 업데이트

        # 엣지 추가 - 순차 실행 흐름
        workflow.add_edge("retrieve_context", "prepare_messages")
        workflow.add_edge("prepare_messages", "generate_response")
        workflow.add_edge("generate_response", "update_state")

        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("update_state", END)

        # 그래프 컴파일
        self.graph = workflow.compile()

    def _retrieve_context(self, state: AnalysisAgentState) -> AnalysisAgentState:

        # k=0이면 검색 비활성화
        if self.k <= 0:
            return state

        if self.role == AnalysisAgentType.REGIONAL_ANALYZER:
            
            # 후보 지역
            recommended_area = state['analysis_result'][AnalysisAgentType.DATA_COLLECTOR]

            # RAG 검색 결과를 저장할 딕셔너리 초기화
            state["context"] = {}
            state["docs"] = {}

            # 각 후보 지역에 대해 상세 검색 수행
            for area in recommended_area:

                area_name = area['area_name']

                # 후보 지역에 대한 상세 검색 쿼리 생성
                query = f"""{area_name} 지역에 대한 교통, 교육, 상업시설, 자연환경, 치안 특징"""

                # RAG 서비스를 통해 검색 실행
                docs_for_area = search_topic(area_name, self.role, query, k=self.k)
                
                # 검색 결과를 state['docs']에 area_name 별로 저장
                state["docs"][area_name] = ([doc.page_content for doc in docs_for_area] if docs_for_area else [])

                # 컨텍스트 포맷팅
                context = self._format_context(docs_for_area)
                state["context"][area_name] = context

        elif self.role == AnalysisAgentType.BUDGET_OPTIMIZER:
            
            # 후보 지역
            recommended_area = state['analysis_result'][AnalysisAgentType.DATA_COLLECTOR]

            # 각 후보 지역에 대해 상세 검색 수행
            for area in recommended_area:

                area_name = area['area_name']

                # RAG 서비스를 통해 검색 실행
                docs_for_price = search_csv(area_name, k=self.k)
                
                # 컨텍스트 포맷팅
                state["context"][area_name] = docs_for_price


        # 상태 업데이트
        return state
    
    # 검색 결과로 Context 생성
    def _format_context(self, docs: list) -> str:

        context = ""
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown")
            section = doc.metadata.get("section", "")
            context += f"[문서 {i + 1}] 출처: {source}"
            if section:
                context += f", 섹션: {section}"
            context += f"\n{doc.page_content}\n\n"
        return context

    # 프롬프트 메시지 준비
    def _prepare_messages(self, state: AnalysisAgentState) -> AnalysisAgentState:

        # 시스템 프롬프트로 시작
        message = [SystemMessage(content=self.system_prompt)]

        # 프롬프트 생성
        prompt = self._create_prompt(state)
        message.append(HumanMessage(content=prompt))

        # 상태 업데이트
        state["message"] = message

        return state

    # 프롬프트 생성 - 하위 클래스에서 구현 필요
    @abstractmethod
    def _create_prompt(self, state: Dict[str, Any]) -> str:
        pass

    # LLM 호출
    def _generate_response(self, state: AnalysisAgentState) -> AnalysisAgentState:

        message = state["message"]
        response = get_llm().invoke(message)

        # 상태 업데이트
        state["response"] = response
        return state
    
    # LLM 응답 처리
    @abstractmethod
    def _handle_response(self, state: Dict[str, Any]) -> str:
        pass

    # 상태 업데이트
    def _update_state(self, state: AnalysisAgentState) -> AnalysisAgentState:

        message = state["message"]
        state["message"] = message[1].content

        response = state["response"]
        state["response"] = response.content

        self._handle_response(state)

        # 상태 업데이트
        return state

    # 분석 실행
    def run(self, state: AnalysisState) -> AnalysisState:
        
        print(f"-------------------- run start ({self.role}) --------------------")
        print(state)
        print("")

        # 초기 에이전트 상태 구성
        agent_state = AnalysisAgentState(
            survey_data=state["survey_data"], 
            message="",
            response="",
            context={},
            docs=state["docs"],
            analysis_result=state["analysis_result"]
        )

        # 내부 그래프 실행
        langfuse_handler = CallbackHandler(session_id=self.session_id)
        result = self.graph.invoke(
            agent_state, config={"callbacks": [langfuse_handler]}
        )

        state["response"] = result["analysis_result"][self.role]
        state["docs"] = result["docs"]
        state["analysis_result"] = result["analysis_result"]

        print(f"-------------------- run end ({self.role}) --------------------")
        print(state)
        print("")

        # 최종 상태 반환
        return state