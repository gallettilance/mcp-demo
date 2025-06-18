from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict, Tuple
from threading import Lock
from uuid import uuid4

app = FastAPI()

class Decision(str, Enum):
    approved = "approved"
    rejected = "rejected"

class ApprovalQuery(BaseModel):
    session_id: str
    tool_name: str

# Shared state and lock for thread safety
approval_store: Dict[Tuple[str, str], Decision] = {}
approval_lock = Lock()

# ---------- Models ----------

class ApprovalRequest(BaseModel):
    session_id: str
    tool_name: str
    decision: Decision | None

class ApprovalResponse(BaseModel):
    status: Optional[Decision]


@app.post("/approve_tool")
def approve_tool(req: ApprovalRequest):
    key = (req.session_id, req.tool_name)
    with approval_lock:
        approval_store[key] = req.decision
    return {"message": f"Tool '{req.tool_name}' marked as {req.decision}."}

@app.post("/approval_status")
def post_approval_status(req: ApprovalQuery):
    approval_store[(req.session_id, req.tool_name)] = None

@app.get("/approval_status", response_model=ApprovalResponse)
def get_approval_status(req: ApprovalQuery):
    with approval_lock:
        decision = approval_store.get((req.session_id, req.tool_name))
    return {"status": decision}
