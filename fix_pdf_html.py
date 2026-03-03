#!/usr/bin/env python3
"""
Quick script to fix missing html_preview for existing PDFs
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / 'backend'))

from app.core.database import SessionLocal
from app.models.parsing_job import ParsingJob
from sqlalchemy import select
from app.services.parser.extract_text import extract_text
from app.services.parser.normalize import normalize_resume_text

def fix_pdf_html():
    session = SessionLocal()
    try:
        # Get all PDF jobs that don't have html_preview
        pdf_jobs = session.execute(
            select(ParsingJob)
            .where(ParsingJob.filename.like('%.pdf'))
            .where(ParsingJob.status == 'success')
        ).scalars().all()
        
        fixed_count = 0
        for job in pdf_jobs:
            parsed_data = job.parsed_data or {}
            debug_data = parsed_data.get('debug', {})
            
            if not debug_data.get('html_preview'):
                print(f'Fixing HTML preview for: {job.filename} (ID: {job.id})')
                
                # Get file path and extract HTML
                file_path = None
                if job.original_file_copy_path and Path(job.original_file_copy_path).exists():
                    file_path = Path(job.original_file_copy_path)
                elif job.file_path.startswith('s3://'):
                    print(f'Skipping S3 file: {job.file_path}')
                    continue
                else:
                    file_path = Path(job.file_path)
                    
                if file_path and file_path.exists():
                    # Extract text and generate HTML
                    extracted = extract_text(file_path)
                    html_preview = extracted.debug.get('html_preview') if extracted.debug else None
                    
                    if html_preview:
                        # Update parsed_data with html_preview
                        debug_data['html_preview'] = html_preview
                        parsed_data['debug'] = debug_data
                        job.parsed_data = parsed_data
                        session.commit()
                        fixed_count += 1
                        print(f'✓ Fixed HTML preview for {job.filename}')
                    else:
                        print(f'✗ Failed to generate HTML for {job.filename}')
                else:
                    print(f'✗ File not found: {file_path}')
            else:
                print(f'✓ Already has HTML preview: {job.filename}')
        
        print(f'\nFixed {fixed_count} PDF files with HTML preview')
        
    finally:
        session.close()

if __name__ == '__main__':
    fix_pdf_html()
