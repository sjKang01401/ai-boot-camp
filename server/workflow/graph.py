from workflow.agents.data_collector_agent import DataCollectorAgent
from workflow.agents.regional_analyzer_agent import RegionalAnalyzerAgent
from workflow.agents.budget_optimizer_agent import BudgetOptimizerAgent
from workflow.agents.recommendation_agent import RecommendationAgent
from workflow.state import AnalysisState, AnalysisAgentType
from langgraph.graph import StateGraph, END


def create_analysis_graph(enable_rag: bool = True, session_id: str = ""):

    # 그래프 생성
    workflow = StateGraph(AnalysisState)

    # 에이전트 인스턴스 생성 - enable_rag에 따라 검색 문서 수 결정
    k_value = 2 if enable_rag else 0
    data_collector = DataCollectorAgent(k=k_value, session_id=session_id)
    regional_analyzer = RegionalAnalyzerAgent(session_id=session_id)
    budget_optimizer = BudgetOptimizerAgent(session_id=session_id)
    recommendation_agent = RecommendationAgent(session_id=session_id)

    # 노드 추가
    workflow.add_node(AnalysisAgentType.DATA_COLLECTOR, data_collector.run)
    workflow.add_node(AnalysisAgentType.REGIONAL_ANALYZER, regional_analyzer.run)
    workflow.add_node(AnalysisAgentType.BUDGET_OPTIMIZER, budget_optimizer.run)
    workflow.add_node(AnalysisAgentType.RECOMMENDATION_SYNTHESIZER, recommendation_agent.run)

    # 엣지 추가
    workflow.set_entry_point(AnalysisAgentType.DATA_COLLECTOR)
    workflow.add_edge(AnalysisAgentType.DATA_COLLECTOR, AnalysisAgentType.REGIONAL_ANALYZER)
    workflow.add_edge(AnalysisAgentType.REGIONAL_ANALYZER, AnalysisAgentType.BUDGET_OPTIMIZER)
    workflow.add_edge(AnalysisAgentType.BUDGET_OPTIMIZER, AnalysisAgentType.RECOMMENDATION_SYNTHESIZER)
    workflow.add_edge(AnalysisAgentType.RECOMMENDATION_SYNTHESIZER, END)

    # 그래프 컴파일
    return workflow.compile()


if __name__ == "__main__":

    graph = create_analysis_graph(True)

    graph_image = graph.get_graph().draw_mermaid_png()

    output_path = "analysis_graph.png"
    with open(output_path, "wb") as f:
        f.write(graph_image)

    import subprocess

    subprocess.run(["open", output_path])
