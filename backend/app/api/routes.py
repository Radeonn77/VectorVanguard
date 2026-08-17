from fastapi import APIRouter
from pydantic import BaseModel

from app.services.agent import run_agent


router = APIRouter()


class InvestigationRequest(BaseModel):
    query: str


class InvestigationResponse(BaseModel):
    answer: str


@router.post(
    "/investigate",
    response_model=InvestigationResponse,
)
def investigate(
    request: InvestigationRequest,
):

    answer = run_agent(
        request.query
    )

    return {
        "answer": answer
    }