from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="Chat session id")
    question: str = Field(..., min_length=3, description="Insurance user query")
    file_ids: List[str] = Field(default_factory=list, description="Uploaded file IDs")
    context: Optional[Dict[str, str]] = Field(default_factory=dict)
    generate_image: bool = Field(default=False)


class HandoffEvent(BaseModel):
    from_agent: str
    to_agent: str
    reason: str
    payload_preview: str


class AgentState(BaseModel):
    request_id: str
    question: str
    retrieved_facts: List[str] = Field(default_factory=list)
    draft: Optional[str] = None
    final_output: Optional[str] = None
    status: str = "created"


class WorkflowResponse(BaseModel):
    request_id: str
    session_id: str
    status: str
    handoffs: List[HandoffEvent]
    state: AgentState
    image_url: Optional[str] = None


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    content_type: Optional[str]
    size: int


class SessionCreateResponse(BaseModel):
    session_id: str


class ImageRequest(BaseModel):
    prompt: str = Field(..., min_length=3)


class ImageResponse(BaseModel):
    image_url: str
