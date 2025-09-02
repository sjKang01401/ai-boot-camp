import streamlit as st
from langchain.schema import Document
from typing import List
from duckduckgo_search import DDGS
from langchain.schema import HumanMessage, SystemMessage
from utils.config import get_llm
from dotenv import load_dotenv

load_dotenv()

def improve_search_query(
    area_data: str,
) -> List[str]:

    prompt = f"{area_data} 지역에 대한 교통, 교육, 상업시설, 자연환경, 치안에 대해 찾고자 한다. 웹검색에 적합한 3개의 검색어를 제안해주세요. 각 검색어는 25자 이내로 작성하고 콤마로 구분하세요. 검색어만 제공하고 설명은 하지 마세요."

    messages = [
        SystemMessage(
            content="당신은 검색 전문가입니다. 주어진 조건에 맞게 정확한 사실을 기반하여 검색해주세요."
        ),
        HumanMessage(content=prompt),
    ]

    # 스트리밍 응답 받기
    response = get_llm().invoke(messages)

    # ,로 구분된 검색어 추출
    suggested_queries = [q.strip() for q in response.content.split(",")]

    return suggested_queries[:3]


def get_search_content(
    improved_queries: str,
    language: str = "ko",
    max_results: int = 5,
) -> List[Document]:

    try:
        documents = []

        ddgs = DDGS()

        # 각 개선된 검색어에 대해 검색 수행
        for query in improved_queries:
            try:
                # 검색 수행
                results = ddgs.text(
                    query,
                    region=language,
                    safesearch="moderate",
                    timelimit="y",  # 최근 1년 내 결과
                    max_results=max_results,
                )

                if not results:
                    continue

                # 검색 결과 처리
                for result in results:
                    title = result.get("title", "")
                    body = result.get("body", "")
                    url = result.get("href", "")

                    if body:
                        documents.append(
                            Document(
                                page_content=body,
                                metadata={
                                    "source": url,
                                    "section": "content",
                                    "topic": title,
                                    "query": query,
                                },
                            )
                        )

            except Exception as e:
                st.warning(f"검색 중 오류 발생: {str(e)}")

        return documents

    except Exception as e:
        st.error(f"검색 서비스 오류 발생: {str(e)}")
        return []
