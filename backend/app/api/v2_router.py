import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.v2_analysis_service import V2AnalysisService

router = APIRouter()
_v2_service: Optional[V2AnalysisService] = None


def get_v2_service() -> V2AnalysisService:
    global _v2_service
    if _v2_service is None:
        _v2_service = V2AnalysisService()
    return _v2_service


class SessionCreateRequest(BaseModel):
    title: Optional[str] = None


class MultiInputItem(BaseModel):
    type: str = Field("event", description="event/data/news/query")
    content: str = Field(..., min_length=1)


class SynthesizeRequest(BaseModel):
    inputs: List[MultiInputItem]
    find_connections: bool = True
    discover_targets: bool = True
    max_depth: int = Field(5, ge=1, le=8)


class DeepAnalyzeRequest(BaseModel):
    seed_query: str = Field(..., min_length=1)
    max_depth: int = Field(5, ge=1, le=8)
    max_nodes: int = Field(50, ge=5, le=200)


class ExpandRequest(BaseModel):
    node_id: str
    direction: str = Field("both", pattern="^(causes|effects|both|related)$")


class AddInputRequest(BaseModel):
    input: MultiInputItem


class SuggestionRequest(BaseModel):
    text: str = ""


def _sse_response(generator):
    async def event_generator():
        try:
            async for event in generator:
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as exc:
            payload = {"status": "error", "message": str(exc), "data": {}}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/sessions")
async def create_session(request: SessionCreateRequest):
    return get_v2_service().create_session(request.title)


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    try:
        return get_v2_service().get_session(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/sessions/{session_id}/analyze-deep")
async def analyze_deep(session_id: str, request: DeepAnalyzeRequest):
    service = get_v2_service()
    return _sse_response(
        service.analyze_deep_stream(
            session_id=session_id,
            seed_query=request.seed_query,
            max_depth=request.max_depth,
            max_nodes=request.max_nodes,
        )
    )


@router.post("/sessions/{session_id}/synthesize")
async def synthesize(session_id: str, request: SynthesizeRequest):
    service = get_v2_service()
    return _sse_response(
        service.synthesize_stream(
            session_id=session_id,
            inputs=[item.model_dump() for item in request.inputs],
            max_depth=request.max_depth,
            find_connections=request.find_connections,
            discover_targets=request.discover_targets,
        )
    )


@router.post("/sessions/{session_id}/expand")
async def expand(session_id: str, request: ExpandRequest):
    try:
        direction = "both" if request.direction == "related" else request.direction
        return await get_v2_service().expand_node(session_id, request.node_id, direction)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/sessions/{session_id}/add-input")
async def add_input(session_id: str, request: AddInputRequest):
    try:
        return get_v2_service().add_input(session_id, request.input.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/sessions/{session_id}/undo")
async def undo(session_id: str):
    try:
        return get_v2_service().undo(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/sessions/{session_id}/graph")
async def get_graph(session_id: str):
    try:
        return get_v2_service().get_session(session_id).get("graph", {})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/sessions/{session_id}/data/refresh/{node_id}")
async def refresh_session_node_data(session_id: str, node_id: str):
    try:
        return await get_v2_service().refresh_node_data(session_id, node_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/data/refresh/{node_id}")
async def refresh_node_data(node_id: str, payload: Dict[str, Any]):
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    return await refresh_session_node_data(session_id, node_id)


@router.post("/suggestions")
async def suggestions(request: SuggestionRequest):
    return await get_v2_service().suggestions(request.text)
