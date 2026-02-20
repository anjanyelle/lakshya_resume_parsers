@echo off
cd /d "%~dp0"
REM Use py -3 (not python) so we don't hit the removed venv
py -3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
