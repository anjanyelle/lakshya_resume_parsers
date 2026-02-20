from app.services.parser.section_parser import SectionParser


def test_section_parser_detects_headers():
    text = """
    John Doe
    Contact Information
    john@example.com | +1-555-555-0100

    Professional Summary
    Experienced backend engineer with 6 years of experience.

    Work Experience
    Example Corp - Software Engineer (2020-2024)
    Built data pipelines.

    Education
    State University - B.Sc Computer Science

    Skills
    Python, SQL, AWS
    """
    parser = SectionParser(use_spacy=False)
    sections = parser.parse(text)

    assert "contact" in sections
    assert "summary" in sections
    assert "experience" in sections
    assert "education" in sections
    assert "skills" in sections
    assert sections["experience"].confidence >= 0.6


def test_section_parser_non_english_headers():
    text = """
    Datos personales
    juan@example.com

    Experiencia Profesional
    Empresa X - Ingeniero

    Educación
    Universidad Y
    """
    parser = SectionParser(use_spacy=False)
    sections = parser.parse(text)

    assert "contact" in sections
    assert "experience" in sections
    assert "education" in sections


def test_section_parser_truncates_experience_at_stop_heading():
    text = """
    John Doe
    Work Experience
    Example Corp - Software Engineer
    Jan 2020 - Feb 2022
    - Built APIs
    - Improved latency

    Skills
    Python, SQL, AWS

    Education
    State University
    """
    parser = SectionParser(use_spacy=False)
    sections = parser.parse(text)

    assert "experience" in sections
    exp = sections["experience"].content
    assert "Example Corp" in exp
    assert "- Built APIs" in exp
    assert "Skills" not in exp
    assert "Python, SQL, AWS" not in exp
    assert sections["experience"].confidence >= 0.6
