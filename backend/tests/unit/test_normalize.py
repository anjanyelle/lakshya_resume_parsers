from app.services.parser.normalize import (
    clean_summary_and_skills_sections,
    fix_ocr_errors,
    normalize_text,
)


def test_normalize_text_collapses_spaces_and_lines():
    text = "Hello   world\r\n\r\n\r\nThis   is  a test"
    normalized = normalize_text(text)
    assert "  " not in normalized
    assert "\n\n\n" not in normalized


def test_fix_ocr_errors_replacements():
    text = "S0ftware 1O1 l23 I99"
    fixed = fix_ocr_errors(text)
    assert "SOf" in fixed
    assert "101" in fixed
    assert "123" in fixed
    assert "199" in fixed


def test_clean_summary_skills_three_item_comma_line_is_skill_like():
    """A line with 3+ comma-separated items should be treated as skill-like and moved to skills."""
    sections = {
        "summary": {"content": "Python, Java, AWS"},
        "skills": {"content": ""},
    }
    out, counts = clean_summary_and_skills_sections(sections)
    assert counts["moved_summary_to_skills"] >= 1
    assert "Python, Java, AWS" in (out["skills"].get("content") or "")


def test_normalize_resume_text_pdf_repairs_hyphenation():
    from app.services.parser.normalize import normalize_resume_text

    text = "soft-\nware engineer"
    result = normalize_resume_text(text, source_format="pdf")
    assert "software engineer" in result
    assert "soft-\nware" not in result


def test_clean_summary_skills_deduplicates_identical_lines():
    """Summary section with two identical lines outputs the line only once."""
    line = "I am an experienced software engineer with over five years building scalable systems."
    sections = {
        "summary": {"content": f"{line}\n{line}"},
        "skills": {"content": ""},
    }
    out, _ = clean_summary_and_skills_sections(sections)
    content = out["summary"].get("content") or ""
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert lines[0] == line


def test_clean_summary_skills_i_led_sentence_is_sentence_like():
    """'I led a team of 10 engineers' should be sentence-like and moved to summary."""
    sections = {
        "summary": {"content": ""},
        "skills": {"content": "I led a team of 10 engineers"},
    }
    out, counts = clean_summary_and_skills_sections(sections)
    assert counts["moved_skills_to_summary"] >= 1
    assert "I led a team of 10 engineers" in (out["summary"].get("content") or "")
