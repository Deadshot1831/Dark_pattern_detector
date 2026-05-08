import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class ScanStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


def _new_id() -> str:
    return str(uuid.uuid4())


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String, primary_key=True, default=_new_id)
    url = Column(String, nullable=False)
    final_url = Column(String, nullable=True)
    page_title = Column(String, nullable=True)
    status = Column(SqlEnum(ScanStatus), default=ScanStatus.pending, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    html_length = Column(Integer, nullable=True)
    html_path = Column(String, nullable=True)
    full_page_screenshot = Column(String, nullable=True)
    viewport_screenshot = Column(String, nullable=True)
    extracted_data = Column(Text, nullable=True)  # JSON blob from extractor
    total_patterns_found = Column(Integer, nullable=True)
    overall_severity = Column(SqlEnum(Severity), nullable=True)

    detections = relationship(
        "DetectedPattern",
        back_populates="scan",
        cascade="all, delete-orphan",
    )


class DetectedPattern(Base):
    __tablename__ = "detected_patterns"

    id = Column(String, primary_key=True, default=_new_id)
    scan_id = Column(String, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    pattern_type = Column(String, nullable=False, index=True)
    evidence_text = Column(Text, nullable=False)
    evidence_selector = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    severity = Column(SqlEnum(Severity), nullable=False)
    explanation = Column(Text, nullable=False)
    suggested_fix = Column(Text, nullable=False)
    method = Column(String, nullable=False)  # rule | dom | hybrid | llm
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    scan = relationship("Scan", back_populates="detections")
