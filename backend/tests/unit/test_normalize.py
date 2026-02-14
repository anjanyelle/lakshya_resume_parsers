from app.services.parser.normalize import fix_ocr_errors, normalize_text


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
