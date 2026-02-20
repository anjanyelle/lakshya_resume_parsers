# Run the FastAPI app using py -3 (system Python). Do NOT use "python" - it points to the removed venv.
# Usage: .\run.ps1
Set-Location $PSScriptRoot
py -3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
