"""
Lightweight test: run experience extractor on training text resumes + all resumes.
Uses only the standalone extract_experience function — no model loading, no AI calls.
"""
import sys, os, json, re, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# ── ONLY import the pure-regex extractor (no AI model loading) ─────────
from parsers.experience_extractor import extract_experience, DATE_LINE_PATTERN

# ── simple inline section splitter to avoid model load ─────────────────
EXP_HEADERS = re.compile(
    r'^(?:professional\s+experience|work\s+experience|experience|employment'
    r'|career\s+history|work\s+history)\s*:?\s*$',
    re.IGNORECASE | re.MULTILINE
)
EDU_HEADERS = re.compile(
    r'^(?:education|academic|certifications?|skills?|technical\s+skills?'
    r'|professional\s+summary|summary)\s*:?\s*$',
    re.IGNORECASE | re.MULTILINE
)

def split_experience_section(text: str) -> str:
    """Cheaply isolate the experience section from a raw resume."""
    # Find first experience header
    m = EXP_HEADERS.search(text)
    if not m:
        return text   # can't find, use all text
    body = text[m.end():]
    # Cut off at next major section
    m2 = EDU_HEADERS.search(body)
    if m2:
        body = body[:m2.start()]
    return body.strip() or text


def extract_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    return "\n".join(page.extract_text() or "" for page in pdf.pages)
            except Exception as e:
                return f"[PDF error: {e}]"
        elif ext in (".docx", ".doc"):
            try:
                import docx
                doc = docx.Document(file_path)
                return "\n".join(p.text for p in doc.paragraphs)
            except Exception as e:
                return f"[DOCX error: {e}]"
        else:
            return f"[Unsupported: {ext}]"
    except Exception as e:
        return f"[Error: {e}]"


def normalise_jobs(raw_jobs: list) -> list:
    """Map raw extractor output → clean DB-ready JSON records."""
    out = []
    GARBAGE_COMPANY = re.compile(
        r'(?i)^(using\s|developed\s|built\s|created\s|led\s|managed\s|'
        r'responsible\s|java\s+streams|the\s+following)',
    )
    for job in raw_jobs:
        title   = (job.get("job_title") or job.get("title") or "").strip()
        company = (job.get("company_name") or job.get("company") or "").strip()
        # Clean trailing "Present/Current" from title
        title   = re.sub(r'\s{2,}(?:Present|Current|Now)\s*$', '', title, flags=re.IGNORECASE).strip()
        # Reject garbage company names
        if GARBAGE_COMPANY.match(company) or len(company) > 80:
            company = ""
        out.append({
            "job_title":    title,
            "company_name": company,
            "start_date":   job.get("start_date"),
            "end_date":     job.get("end_date"),
            "is_current":   job.get("is_current", False),
            "description":  (job.get("description") or "").strip()[:300] or None,
        })
    return out


def check_quality(jobs: list, file_name: str) -> dict:
    total  = len(jobs)
    issues = []
    score  = 100

    if total == 0:
        return {"quality_score": 0, "jobs_found": 0,
                "issues": ["❌ CRITICAL: No jobs extracted at all"]}

    missing_title   = sum(1 for j in jobs if not j.get("job_title"))
    missing_company = sum(1 for j in jobs if not j.get("company_name"))
    missing_dates   = sum(1 for j in jobs if not j.get("start_date"))
    GARBAGE = re.compile(r'(?i)^(using\s|developed\s|built\s)')
    garbage_company = sum(1 for j in jobs if j.get("company_name") and GARBAGE.match(j["company_name"]))

    score -= missing_title   * 10
    score -= missing_company * 8
    score -= missing_dates   * 5
    score -= garbage_company * 20

    if missing_title:        issues.append(f"⚠️  {missing_title}/{total} jobs have blank job_title")
    if missing_company:      issues.append(f"⚠️  {missing_company}/{total} jobs have blank company_name")
    if missing_dates:        issues.append(f"⚠️  {missing_dates}/{total} jobs have no start_date")
    if garbage_company:      issues.append(f"❌ {garbage_company}/{total} jobs have garbage company_name")
    if not issues:           issues.append("✅ All good")

    return {"quality_score": max(0, score), "jobs_found": total, "issues": issues}


# ═══════════════════════════════════════════════════════════════════════
BASE  = Path(__file__).parent
TEXT_DIR   = BASE / "training" / "data" / "text_resumes"
RESUME_DIR = BASE.parent / "resumes"

all_results = {}
errors      = []

# ── PHASE 1: training text resumes ─────────────────────────────────────
print("=" * 80)
print("🧪  PHASE 1 — TRAINING TEXT RESUMES (ground truth, rule-based only)")
print("=" * 80)

for txt in sorted(TEXT_DIR.glob("*.txt")):
    text    = extract_text(str(txt))
    exp_txt = split_experience_section(text)
    t0      = time.time()
    raw     = extract_experience(exp_txt)
    ms      = (time.time() - t0) * 1000
    jobs    = normalise_jobs(raw)
    q       = check_quality(jobs, txt.name)

    print(f"\n📄  {txt.name}  [{ms:.0f}ms]")
    print(f"    Jobs: {q['jobs_found']}  |  Score: {q['quality_score']}/100")
    for issue in q["issues"]:
        print(f"    {issue}")
    for i, j in enumerate(jobs):
        cur = "▶" if j["is_current"] else " "
        print(f"    {cur}[{i+1}] {(j['job_title'] or '(no title)'):<42} @ "
              f"{(j['company_name'] or '(no company)'):<32} "
              f"{j['start_date'] or '?'} → {j['end_date'] or 'Present'}")
    all_results[txt.name] = {"jobs": jobs, "quality": q}


# ── PHASE 2: real resumes ───────────────────────────────────────────────
print("\n" + "=" * 80)
print("🧪  PHASE 2 — ACTUAL RESUMES /resumes folder")
print("=" * 80)

resume_files = sorted([
    f for f in RESUME_DIR.iterdir()
    if f.suffix.lower() in (".pdf", ".docx", ".doc", ".txt")
    and not f.name.startswith("~")
    and f.name != "README.md"
])

for rf in resume_files:
    text = extract_text(str(rf))
    if text.startswith("["):
        print(f"\n📄  {rf.name}\n    {text}")
        errors.append({"file": rf.name, "error": text})
        continue

    exp_txt = split_experience_section(text)
    t0      = time.time()
    raw     = extract_experience(exp_txt)
    ms      = (time.time() - t0) * 1000
    jobs    = normalise_jobs(raw)
    q       = check_quality(jobs, rf.name)

    print(f"\n📄  {rf.name}  [{ms:.0f}ms]")
    print(f"    Jobs: {q['jobs_found']}  |  Score: {q['quality_score']}/100")
    for issue in q["issues"]:
        print(f"    {issue}")
    for i, j in enumerate(jobs):
        cur = "▶" if j["is_current"] else " "
        print(f"    {cur}[{i+1}] {(j['job_title'] or '(no title)'):<42} @ "
              f"{(j['company_name'] or '(no company)'):<32} "
              f"{j['start_date'] or '?'} → {j['end_date'] or 'Present'}")
    all_results[rf.name] = {"jobs": jobs, "quality": q}


# ── save results ────────────────────────────────────────────────────────
out_path = BASE / "test_results.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, default=str)

# ── summary ─────────────────────────────────────────────────────────────
total    = len(all_results)
perfect  = sum(1 for v in all_results.values() if v["quality"]["quality_score"] >= 80)
good     = sum(1 for v in all_results.values() if 50 <= v["quality"]["quality_score"] < 80)
poor     = sum(1 for v in all_results.values() if v["quality"]["quality_score"] < 50)
zero_jobs = [k for k, v in all_results.items() if v["quality"]["jobs_found"] == 0]

print("\n" + "=" * 80)
print("📊  SUMMARY")
print("=" * 80)
print(f"  Total files : {total}")
print(f"  ✅ Excellent (≥80): {perfect}")
print(f"  🟡 Good  (50–79):  {good}")
print(f"  ❌ Poor  (<50):    {poor}")
if zero_jobs:
    print(f"\n  🚨 Files with ZERO jobs extracted:")
    for z in zero_jobs:
        print(f"     - {z}")
if errors:
    print(f"\n  ⚠️  Files that could not be read: {len(errors)}")
    for e in errors:
        print(f"     - {e['file']}: {e['error'][:80]}")
print(f"\n  Full results → {out_path}")
print("=" * 80)
