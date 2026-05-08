import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..crawler.playwright_crawler import crawl_url
from ..db.database import SessionLocal, get_db
from ..db.models import Scan, ScanStatus
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

            scan.final_url = result.final_url
            scan.page_title = result.title
            scan.html_length = len(result.html)
            scan.html_path = str(html_path.relative_to(STORAGE_DIR))
            scan.full_page_screenshot = str(result.full_page_screenshot.relative_to(STORAGE_DIR))
            scan.viewport_screenshot = str(result.viewport_screenshot.relative_to(STORAGE_DIR))
            scan.extracted_data = json.dumps(extracted.to_dict())
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
