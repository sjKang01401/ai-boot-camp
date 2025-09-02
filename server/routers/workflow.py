from typing import Any
import uuid
import json
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langfuse.callback import CallbackHandler
from sqlalchemy.orm import Session

from db.database import get_db
from db import crud

from workflow.state import AnalysisState
from workflow.graph import create_analysis_graph


# API 경로를 /api/v1로 변경
router = APIRouter(
    prefix="/api/v1/workflow",
    tags=["workflow"],
    responses={404: {"description": "Not found"}},
)

async def analysis_generator(analysis_graph, initial_state, langfuse_handler):
    # 그래프에서 청크 스트리밍
    async for chunk in analysis_graph.astream(
        initial_state,
        config={"callbacks": [langfuse_handler]},
        # subgraphs=True,
        # stream_mode="updates",
    ):
        if not chunk:
            continue

        for key, value in chunk.items():

            # print("start workflow analysis_generator ----------------------------------------")
            # print(value)
            # print("end workflow analysis_generator ----------------------------------------")

            state = {
                "role": key,
                "response": value["response"],
                "docs": value.get("docs", {}),
            }

            event_data = {"type": "update", "data": state}
            yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.01)

    # 분석 종료 메시지
    yield f"data: {json.dumps({'type': 'end', 'data': {}}, ensure_ascii=False)}\n\n"

@router.post("/analysis/{survey_id}")
async def start_analysis_workflow(survey_id: int, db: Session = Depends(get_db)):

    # 설문 정보 불러오기
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    session_id = str(uuid.uuid4())
    analysis_graph = create_analysis_graph(survey.to_dict(), session_id)

    initial_state: AnalysisState = {
        "survey_data": survey.to_dict(), 
        "role": "",
        "response": "",
        "docs": {},
        "analysis_result": {}
    }

    langfuse_handler = CallbackHandler(session_id=session_id)

    return StreamingResponse(
        analysis_generator(analysis_graph, initial_state, langfuse_handler),
        media_type="text/event-stream",
    )
