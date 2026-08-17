from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.evidence import EvidenceRecord
from app.core.vector_store import collection


def store_evidence(
    db: Session,
    evidence_id: str,
    session_id: int,
    image_path: str,
    ocr_text: str,
    timestamp: datetime | None = None,
):
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    # PostgreSQL
    evidence = EvidenceRecord(
        evidence_id=evidence_id,
        session_id=session_id,
        image_path=image_path,
        ocr_text=ocr_text,
        timestamp=timestamp,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    # ChromaDB
    collection.add(
        ids=[evidence_id],
        documents=[ocr_text],
        metadatas=[
            {
                "evidence_id": evidence_id,
                "session_id": str(session_id),
            }
        ],
    )

    return evidence