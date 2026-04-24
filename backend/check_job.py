import uuid
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.parsing_job import ParsingJob

job_id = "278d5b06-1b63-4ee2-8ae1-d101ba94957f"

session = SessionLocal()
try:
    job = session.execute(select(ParsingJob).where(ParsingJob.id == uuid.UUID(job_id))).scalar_one_or_none()
    if job:
        print(f"Job found: {job.id}")
        print(f"Raw Text Length: {len(job.raw_text) if job.raw_text else 'None'}")
        print(f"Parsed Data exists: {bool(job.parsed_data)}")
        if job.parsed_data:
            debug = job.parsed_data.get("debug", {})
            html_preview = debug.get("html_preview")
            print(f"HTML Preview Length: {len(html_preview) if html_preview else 'None'}")
    else:
        print("Job not found")
finally:
    session.close()
