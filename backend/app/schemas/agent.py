from typing import Any

from pydantic import BaseModel, Field


class AgentDebugOptions(BaseModel):
    dry_run: bool = False
    explain: bool = False


class AgentMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    conversation_id: str | None = None
    debug: AgentDebugOptions = Field(default_factory=AgentDebugOptions)


class TraceStep(BaseModel):
    kind: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class ToolCallTrace(BaseModel):
    name: str
    args: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | None = None
    error: str | None = None


class AgentDebugTrace(BaseModel):
    trace_id: str
    conversation_id: str | None = None
    intent: str
    candidate_tools: list[str] = Field(default_factory=list)
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)
    steps: list[TraceStep] = Field(default_factory=list)
    dry_run: bool = False
    explain: bool = False


class AgentMessageResponse(BaseModel):
    trace_id: str
    reply: str
    debug_trace: AgentDebugTrace | None = None
