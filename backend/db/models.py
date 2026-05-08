import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer, String, Text

from .database import Base


class ScanStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


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
