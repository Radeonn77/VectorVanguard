from pathlib import Path
from uuid import uuid4

import cv2
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.agent import run_agent
from app.services.ingestion import ingest_evidence


router = APIRouter()


UPLOAD_DIRECTORY = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "data"
    / "raw"
)

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


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


@router.post("/upload-evidence")
async def upload_evidence(
    session_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format.",
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid image content type.",
        )

    file_data = await file.read()

    if not file_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 10 MB limit.",
        )

    evidence_id = f"EVD-{uuid4().hex[:12]}"

    filename = f"{evidence_id}{extension}"

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_path = (
        UPLOAD_DIRECTORY / filename
    )

    image_path.write_bytes(file_data)

    image = cv2.imread(str(image_path))

    if image is None:
        image_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid readable image.",
        )

    try:
        evidence = ingest_evidence(
            db=db,
            session_id=session_id,
            image_path=str(image_path),
            evidence_id=evidence_id,
        )

    except Exception as exc:
        db.rollback()
        image_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=f"Evidence processing failed: {exc}",
        )

    return {
        "message": "Evidence uploaded and processed successfully.",
        "evidence_id": evidence.evidence_id,
        "session_id": evidence.session_id,
        "image_path": evidence.image_path,
        "ocr_text": evidence.ocr_text,
    }