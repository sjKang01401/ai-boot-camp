import os
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from utils.config import settings
from typing import Any, Dict, Optional, List
from retrieval.search_service import get_search_content, improve_search_query
from utils.config import get_embeddings, get_llm

def get_topic_vector_store(
    area_name: str, role: str, language: str = "ko"
) -> Optional[FAISS]:

    # 검색어 개선
    improved_queries = improve_search_query(area_name)
    # 개선된 검색어로 검색 콘텐츠 가져오기
    documents = get_search_content(improved_queries, language)
    if not documents:
        return None
    try:
        return FAISS.from_documents(documents, get_embeddings())
    except Exception as e:
        st.error(f"Vector DB 생성 중 오류 발생: {str(e)}")
        return None

def search_topic(area_name: str, role: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
    # 문서를 검색해서 벡터 스토어 생성
    vector_store = get_topic_vector_store(area_name, role)
    if not vector_store:
        return []
    try:
        # 벡터 스토어에서 Similarity Search 수행
        return vector_store.similarity_search(query, k=k)
    except Exception as e:
        st.error(f"검색 중 오류 발생: {str(e)}")
        return []

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "apartment_trading_prices_20250713192258.csv")

# 단계 1: 문서 로드(Load Documents)
loader = CSVLoader(
    file_path=csv_path,
    encoding="euc-kr",
    csv_args={
        'delimiter': ',',  # 구분자
        'quotechar': '"',  # 따옴표
        'skipinitialspace': True
    }
)
docs = loader.load()

# 단계 2: 문서 분할(Split Documents)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
split_documents = text_splitter.split_documents(docs)

# 단계 4: DB 생성(Create DB) 및 저장
# 벡터스토어를 생성합니다.
vectorstore = FAISS.from_documents(documents=split_documents, embedding=get_embeddings())

# 단계 5: 검색기(Retriever) 생성
# 문서에 포함되어 있는 정보를 검색하고 생성합니다.
retriever = vectorstore.as_retriever()
print("CSV 로딩 완료")

def search_csv(area_name: str, k: int = 5) -> List[Dict[str, Any]]:
    
    # 단계 6: 프롬프트 생성(Create Prompt)
    # 프롬프트를 생성합니다.
    prompt = PromptTemplate.from_template(
        """검색된 컨텍스트를 사용하여 질문에 답하세요.
        답변 예시를 참고하여 답변을 출력하고, 다른 설명은 추가하지 마세요. 
        데이터가 없어서 답하지 못하는 경우에는 '정보 없음' 이라고 답해주세요.

        #컨텍스트:
        {context}

        #질문:
        {area_name} 지역에 대한 아파트 매매 실거래가 평균

        #답변 예시:
        2024년 하반기 ~ 2025년 상반기의 {area_name} 지역의 아파트 매매 실거래가 평균은 180,000 만원 입니다.
        """
    )

    chain = (
    {"context": retriever, "area_name": RunnablePassthrough()}
        | prompt
        | get_llm()
        | StrOutputParser()
    )

    response = chain.invoke(area_name)
    print(response)