import base64
from datetime import datetime, timezone
from pathlib import Path

import cv2
import pytesseract
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.evidence_store import store_evidence


TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


vision_llm = ChatOllama(
    model=settings.OLLAMA_VISION_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0,
)


def preprocess_image(image_path: str) -> object:
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    grayscale = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    _, thresholded = cv2.threshold(
        grayscale,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    return thresholded


def extract_ocr(image_path: str) -> str:
    processed_image = preprocess_image(
        image_path
    )

    text = pytesseract.image_to_string(
        processed_image
    )

    return text.strip()


def analyze_image(image_path: str) -> str:
    image_path = Path(image_path)

    suffix = image_path.suffix.lower()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    mime_type = mime_types.get(
        suffix,
        "image/jpeg",
    )

    with image_path.open("rb") as image_file:
        image_data = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Analyze this exam evidence image. "
                    "Describe visible people, objects, "
                    "devices, documents, and relevant "
                    "exam-environment details. "
                    "Do not guess details that are not visible."
                ),
            },
            {
                "type": "image_url",
                "image_url": (
                    f"data:{mime_type};base64,{image_data}"
                ),
            },
        ],
    )

    response = vision_llm.invoke([message])

    return str(response.content).strip()


def ingest_evidence(
    db: Session,
    session_id: int,
    image_path: str,
    evidence_id: str,
):
    ocr_text = extract_ocr(
        image_path
    )

    vision_description = analyze_image(
        image_path
    )

    combined_text = (
        f"OCR:\n"
        f"{ocr_text}\n\n"
        f"VISION:\n"
        f"{vision_description}"
    )

    try:
        evidence = store_evidence(
            db=db,
            evidence_id=evidence_id,
            session_id=session_id,
            image_path=image_path,
            ocr_text=combined_text,
            timestamp=datetime.now(timezone.utc),
        )

        return evidence

    except Exception:
        db.rollback()
        raise