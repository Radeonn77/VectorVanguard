from app.core.database import SessionLocal
from app.services.evidence_store import store_evidence
from app.models.student import Student
from app.models.exam_session import ExamSession
from app.core.vector_store import collection


TEST_STUDENT_ID = "BRIDGE-TEST-001"
TEST_EVIDENCE_ID = "EV-BRIDGE-TEST-001"


db = SessionLocal()

try:
    # Create test student
    student = Student(
        student_id=TEST_STUDENT_ID,
        name="Bridge Test Student",
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    # Create test exam session
    session = ExamSession(
        student_id=student.id,
        exam_name="Bridge Test Exam",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    # Store evidence in PostgreSQL + ChromaDB
    evidence = store_evidence(
        db=db,
        evidence_id=TEST_EVIDENCE_ID,
        session_id=session.id,
        image_path="data/raw/bridge_test.jpg",
        ocr_text="A mobile phone was visible near the student.",
    )

    print("[1] PostgreSQL evidence_id:", evidence.evidence_id)

    # Search ChromaDB
    result = collection.get(
        ids=[TEST_EVIDENCE_ID]
    )

    print("[2] ChromaDB ID:", result["ids"][0])
    print("[3] ChromaDB metadata:", result["metadatas"][0])

    if (
        evidence.evidence_id == result["ids"][0]
        and result["metadatas"][0]["evidence_id"] == TEST_EVIDENCE_ID
    ):
        print("\n[SUCCESS] PostgreSQL ↔ ChromaDB bridge verified.")
    else:
        print("\n[ERROR] Bridge verification failed.")

finally:
    db.close()