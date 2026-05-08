import json
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..classifier.llm_classifier import enrich as llm_enrich
from ..crawler.playwright_crawler import crawl_url
from ..db.database import SessionLocal, get_db
from ..db.models import DetectedPattern, Scan, ScanStatus, Severity
from ..detectors.base import overall_severity
from ..detectors.registry import run_all as run_detectors
from ..extractor.section_extractor import extract as extract_page
from ..utils.url_validator import InvalidURLError, validate_url

router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = PROJECT_ROOT / "storage"


class ScanCreateRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    url: str
    final_url: Optional[str] = None
    page_title: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    full_page_screenshot_url: Optional[str] = None
    viewport_screenshot_url: Optional[str] = None
    total_patterns_found: Optional[int] = None
    overall_severity: Optional[str] = None


class DetectionView(BaseModel):
    id: str
    pattern_type: str
    evidence_text: str
    evidence_selector: Optional[str] = None
    confidence: float
    severity: str
    explanation: str
    suggested_fix: str
    method: str


def _to_response(scan: Scan) -> ScanResponse:
    base = f"/scan/{scan.id}/screenshot"
    return ScanResponse(
        scan_id=scan.id,
        status=scan.status.value,
        url=scan.url,
        final_url=scan.final_url,
        page_title=scan.page_title,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        error_message=scan.error_message,
        full_page_screenshot_url=f"{base}/full_page" if scan.full_page_screenshot else None,
        viewport_screenshot_url=f"{base}/viewport" if scan.viewport_screenshot else None,
        total_patterns_found=scan.total_patterns_found,
        overall_severity=scan.overall_severity.value if scan.overall_severity else None,
    )


async def _run_crawl(scan_id: str, url: str) -> None:
    db = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        if scan is None:
            return
        scan.status = ScanStatus.running
        db.commit()

        try:
            screenshot_dir = STORAGE_DIR / "screenshots" / scan_id
            result = await crawl_url(url, screenshot_dir)

            html_path = screenshot_dir / "page.html"
            html_path.write_text(result.html, encoding="utf-8")

            extracted = extract_page(result.html, page_title=result.title)
            detections = run_detectors(extracted)
            try:
                llm_additions = await llm_enrich(extracted, detections)
                detections.extend(llm_additions)
            except Exception as e:  # never let LLM break the scan
                scan.error_message = (scan.error_message or "") + f" [llm warning: {type(e).__name__}: {e}]"

            scan.final_url = result.final_url
            scan.page_title = result.title
            scan.html_length = len(result.html)
            scan.html_path = str(html_path.relative_to(STORAGE_DIR))
            scan.full_page_screenshot = str(result.full_page_screenshot.relative_to(STORAGE_DIR))
            scan.viewport_screenshot = str(result.viewport_screenshot.relative_to(STORAGE_DIR))
            scan.extracted_data = json.dumps(extracted.to_dict())
            scan.total_patterns_found = len(detections)
            scan.overall_severity = Severity(overall_severity(detections))
            for d in detections:
                db.add(DetectedPattern(
                    scan_id=scan.id,
                    pattern_type=d.pattern_type,
                    evidence_text=d.evidence_text,
                    evidence_selector=d.evidence_selector or None,
                    confidence=d.confidence,
                    severity=Severity(d.severity),
                    explanation=d.explanation,
                    suggested_fix=d.suggested_fix,
                    method=d.method,
                ))
            scan.status = ScanStatus.completed
            scan.completed_at = datetime.utcnow()
        except Exception as e:
            scan.status = ScanStatus.failed
            scan.error_message = f"{type(e).__name__}: {e}"
            scan.completed_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


@router.post("/scan", response_model=ScanResponse, status_code=201)
async def create_scan(
    payload: ScanCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> ScanResponse:
    try:
        url = validate_url(payload.url)
    except InvalidURLError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    scan = Scan(url=url)
    db.add(scan)
    db.commit()
    db.refresh(scan)

    background_tasks.add_task(_run_crawl, scan.id, url)
    return _to_response(scan)


@router.get("/scan/{scan_id}", response_model=ScanResponse)
def get_scan(scan_id: str, db: Session = Depends(get_db)) -> ScanResponse:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return _to_response(scan)


@router.get("/scan/{scan_id}/detections", response_model=List[DetectionView])
def get_detections(scan_id: str, db: Session = Depends(get_db)) -> List[DetectionView]:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return [
        DetectionView(
            id=d.id,
            pattern_type=d.pattern_type,
            evidence_text=d.evidence_text,
            evidence_selector=d.evidence_selector,
            confidence=d.confidence,
            severity=d.severity.value,
            explanation=d.explanation,
            suggested_fix=d.suggested_fix,
            method=d.method,
        )
        for d in scan.detections
    ]


@router.get("/scan/{scan_id}/extracted")
def get_extracted(scan_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    if not scan.extracted_data:
        raise HTTPException(status_code=404, detail="Extraction not available yet")
    return json.loads(scan.extracted_data)


@router.get("/scan/{scan_id}/screenshot/{kind}")
def get_screenshot(
    scan_id: str, kind: str, db: Session = Depends(get_db)
) -> FileResponse:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    rel = {
        "full_page": scan.full_page_screenshot,
        "viewport": scan.viewport_screenshot,
    }.get(kind)
    if not rel:
        raise HTTPException(status_code=404, detail="Screenshot not available")

    abs_path = STORAGE_DIR / rel
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail="Screenshot file missing")
    return FileResponse(abs_path, media_type="image/png")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
