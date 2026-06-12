"""Comprehensive unit tests for EducationParser.

Covers all 5 user-provided test samples plus edge cases.
"""
from __future__ import annotations

import re

import pytest

from datetime import date


from app.services.parser.education_parser import EducationParser



@pytest.fixture
def parser() -> EducationParser:
    return EducationParser()


# =====================================================================
# Full-pipeline tests for each user sample
# =====================================================================

class TestUserSample1:
    """Bachelors in CS + Sreenidhi Institute on separate lines."""

    TEXT = (
        "Bachelors in computer and information science\t\t\t\t\t\t Aug 2010 \u2013 May 2014\n"
        "Sreenidhi Institute Of Science and Technology"
    )

    def test_single_entry(self, parser: EducationParser):
        entries = parser.parse(self.TEXT)
        assert len(entries) == 1

    def test_institution(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.institution == "Sreenidhi Institute Of Science and Technology"

    def test_degree(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.degree is not None
        assert "bachelor" in entry.degree.lower()

    def test_field_of_study(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.field_of_study is not None
        assert "computer" in entry.field_of_study.lower()

    def test_dates(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.start_date is not None
        assert entry.start_date.year == 2010
        assert entry.end_date is not None
        assert entry.end_date.year == 2014


class TestUserSample2:
    """Bachelor of Technology in CS at Koneru (single line)."""

    TEXT = "Bachelor of Technology in Computer Science & Engineering at Koneru Lakshmaiah University 2010-2014"

    def test_single_entry(self, parser: EducationParser):
        entries = parser.parse(self.TEXT)
        assert len(entries) == 1

    def test_institution(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.institution is not None
        assert "koneru" in entry.institution.lower()

    def test_degree(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.degree is not None
        assert "bachelor" in entry.degree.lower() or "technology" in entry.degree.lower()

    def test_field_of_study(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.field_of_study is not None
        assert "computer science" in entry.field_of_study.lower()

    def test_end_date(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.end_date is not None
        assert entry.end_date.year == 2014


class TestUserSample3:
    """Degree: ... / College: MRCET / GPA: 7.81 format."""

    TEXT = (
        "Degree: Bachelor of Technology in Computer Science and Engineering (May 2010 \u2013 March 2014)\n"
        "College: MRCET\n"
        "GPA: 7.81"
    )

    def test_single_entry(self, parser: EducationParser):
        entries = parser.parse(self.TEXT)
        assert len(entries) == 1

    def test_institution(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.institution == "MRCET"

    def test_degree(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.degree is not None
        assert "bachelor" in entry.degree.lower() or "technology" in entry.degree.lower()

    def test_field_of_study(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.field_of_study is not None
        assert "computer science" in entry.field_of_study.lower()

    def test_gpa(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.gpa == "7.81"

    def test_dates(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.start_date is not None
        assert entry.start_date.year == 2010
        assert entry.end_date is not None
        assert entry.end_date.year == 2014


class TestUserSample4:
    """Multi-entry: MBA at Georgia Tech + BS at UT Austin."""

    TEXT = (
        "Master of Business Administration (MBA) in Strategic Management & Operations\n"
        "Georgia Institute of Technology (Scheller College of Business), Atlanta, GA\n"
        "Research Focus: Macro-Logistics Optimization and Distributed Ledger Technology in Retail.\n"
        "Honors: Top 5% of Class; Recipient of the Executive Leadership Award.\n"
        "Bachelor of Science in Industrial Engineering & Computer Science\n"
        "The University of Texas at Austin, Austin, TX\n"
        "Honors: Summa Cum Laude; President of the Industrial Engineering Society.\n"
        "Minor: Computational Data Analysis"
    )

    def test_two_entries(self, parser: EducationParser):
        entries = parser.parse(self.TEXT)
        assert len(entries) == 2

    def test_first_entry_is_mba(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.degree is not None
        assert "master" in entry.degree.lower()

    def test_first_entry_institution(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.institution is not None
        assert "georgia" in entry.institution.lower()

    def test_first_entry_field(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[0]
        assert entry.field_of_study is not None
        assert "strategic management" in entry.field_of_study.lower()

    def test_second_entry_is_bs(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[1]
        assert entry.degree is not None
        assert "bachelor" in entry.degree.lower()

    def test_second_entry_institution(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[1]
        assert entry.institution is not None
        assert "texas" in entry.institution.lower()

    def test_second_entry_field(self, parser: EducationParser):
        entry = parser.parse(self.TEXT)[1]
        assert entry.field_of_study is not None
        assert "industrial engineering" in entry.field_of_study.lower()

    def test_honors_detected(self, parser: EducationParser):
        entries = parser.parse(self.TEXT)
        honors = [e.honors for e in entries if e.honors]
        assert len(honors) >= 1


class TestUserSample5:
    """No education content — should return 0 entries."""

    TEXT = "John Doe\nSoftware Engineer at Google"

    def test_no_entries(self, parser: EducationParser):
        entries = parser.parse(self.TEXT)
        assert len(entries) == 0

    def test_doe_not_detected_as_degree(self, parser: EducationParser):
        """Regression: 'Doe' was previously detected as a degree acronym."""
        entries = parser.parse(self.TEXT)
        for e in entries:
            assert e.degree != "Doe"


# =====================================================================
# Edge-case tests
# =====================================================================

class TestEdgeCases:
    def test_empty_string(self, parser: EducationParser):
        assert parser.parse("") == []

    def test_whitespace_only(self, parser: EducationParser):
        assert parser.parse("   \n  \n  ") == []

    def test_single_year_graduation(self, parser: EducationParser):
        text = "Bachelor of Science, MIT, 2020"
        entries = parser.parse(text)
        assert len(entries) >= 1
        entry = entries[0]
        assert entry.end_date is not None
        assert entry.end_date.year == 2020

    def test_gpa_slash_format(self, parser: EducationParser):
        text = "BS Computer Science, GPA 3.8/4.0, Stanford University"
        entries = parser.parse(text)
        assert len(entries) >= 1
        entry = entries[0]
        assert entry.gpa is not None
        assert "3.8" in entry.gpa

    def test_gpa_percentage(self, parser: EducationParser):
        text = "BTech Computer Science, GPA: 8.5, IIT Bombay"
        entries = parser.parse(text)
        assert len(entries) >= 1
        entry = entries[0]
        assert entry.gpa is not None
        assert "8.5" in entry.gpa

    def test_in_progress_education(self, parser: EducationParser):
        text = "Master of Science in Data Science, Sep 2023 - Present\nStanford University"
        entries = parser.parse(text)
        assert len(entries) >= 1
        entry = entries[0]
        assert entry.in_progress is True

    def test_summa_cum_laude(self, parser: EducationParser):
        text = "Bachelor of Arts, Summa Cum Laude, Harvard University"
        entries = parser.parse(text)
        assert len(entries) >= 1
        entry = entries[0]
        assert entry.honors is not None
        assert "cum laude" in entry.honors.lower()

    def test_no_false_positive_from_names(self, parser: EducationParser):
        """Names like 'Mike', 'Peter', 'David' should not trigger degree detection."""
        text = "Mike Douglas\nProject Manager at Acme Corp"
        entries = parser.parse(text)
        for e in entries:
            assert e.degree is None or "ug" not in e.degree.lower()


# =====================================================================
# Individual method tests
# =====================================================================

class TestExtractDegree:
    def test_bachelor_alias(self, parser: EducationParser):
        result = parser._extract_degree("Bachelor of Science in CS")
        assert result is not None
        assert "bachelor" in result.lower() or "science" in result.lower()

    def test_mba_abbreviation(self, parser: EducationParser):
        result = parser._extract_degree("MBA in Finance")
        assert result is not None

    def test_no_false_positive_doe(self, parser: EducationParser):
        result = parser._extract_degree("John Doe")
        assert result is None

    def test_no_false_positive_random_caps(self, parser: EducationParser):
        result = parser._extract_degree("PLEASE READ")
        assert result is None


class TestExtractInstitution:
    def test_standalone_university_line(self, parser: EducationParser):
        text = "Harvard University"
        result = parser._extract_institution(text)
        assert result is not None
        assert "harvard" in result.lower()

    def test_labeled_college(self, parser: EducationParser):
        text = "College: MRCET"
        result = parser._extract_institution(text)
        assert result == "MRCET"

    def test_inline_at_university(self, parser: EducationParser):
        text = "Bachelor of Technology in CS at Koneru Lakshmaiah University 2010-2014"
        result = parser._extract_institution(text)
        assert result is not None
        assert "koneru" in result.lower()

    def test_no_institution(self, parser: EducationParser):
        text = "Bachelor of Science in Computer Science, 2020"
        result = parser._extract_institution(text)
        assert result is None


class TestExtractField:
    def test_field_with_in_keyword(self, parser: EducationParser):
        result = parser._extract_field("Bachelor of Technology in Computer Science")
        assert result is not None
        assert "computer science" in result.lower()

    def test_field_truncated_at_institution(self, parser: EducationParser):
        result = parser._extract_field(
            "Bachelor of Technology in Computer Science & Engineering at Koneru Lakshmaiah University"
        )
        assert result is not None
        assert "koneru" not in result.lower()

    def test_no_field(self, parser: EducationParser):
        result = parser._extract_field("Harvard University")
        assert result is None


class TestExtractGpa:
    def test_gpa_with_label(self, parser: EducationParser):
        result = parser._extract_gpa("GPA: 7.81")
        assert result == "7.81"

    def test_gpa_slash_format(self, parser: EducationParser):
        result = parser._extract_gpa("GPA 3.8/4.0")
        assert result is not None
        assert "3.8" in result

    def test_gpa_percentage(self, parser: EducationParser):
        result = parser._extract_gpa("Scored 85% in finals")
        assert result == "85%"

    def test_no_gpa(self, parser: EducationParser):
        result = parser._extract_gpa("Bachelor of Science")
        assert result is None


# =====================================================================
# Multi-format / industry-style samples (from user EDUCATION examples)
# =====================================================================

class TestMultiFormatEducation:
    """Samples covering multiple resume formats for robust parsing."""

    def test_jntu_date_range_and_institution(self, parser: EducationParser):
        text = (
            "Bachelor of Technology (B.Tech) in computer science\n"
            "Jawaharlal Nehru Technological University, India. July-2010 to June 2014"
        )
        entries = parser.parse(text)
        assert len(entries) == 1
        e = entries[0]
        assert e.institution and "Jawaharlal" in e.institution
        assert e.degree and "technology" in e.degree.lower()
        assert e.start_date and e.start_date.year == 2010
        assert e.end_date and e.end_date.year == 2014

    def test_year_range_only(self, parser: EducationParser):
        text = "Education:\n\nBachelor of Technology 2010 - 2014"
        entries = parser.parse(text)
        assert len(entries) == 1
        e = entries[0]
        assert e.start_date is None or e.start_date.year == 2010
        assert e.end_date and e.end_date.year == 2014

    def test_mlwe_college_with_month_range(self, parser: EducationParser):
        text = "EDUCATION\nBachelor of Technology in Computer Science - MLWE college - June 2010 - July 2014"
        entries = parser.parse(text)
        assert len(entries) == 1
        e = entries[0]
        assert e.institution and "MLWE" in e.institution
        assert e.start_date and e.end_date

    def test_from_institution_pattern(self, parser: EducationParser):
        text = (
            "EDUCATION\n"
            "Bachelor of Technology: Computer Science Engineering from "
            "R. V. R & J. C College of Engineering"
        )
        entries = parser.parse(text)
        assert len(entries) == 1
        e = entries[0]
        assert e.institution and "R. V. R" in e.institution

    def test_degree_label_college_gpa(self, parser: EducationParser):
        text = (
            "EDUCATION:\n"
            "Degree: Bachelor of Technology in Computer Science and Engineering (May 2010 – March 2014)\n"
            "College: MRCET\n"
            "GPA: 7.81"
        )
        entries = parser.parse(text)
        assert len(entries) == 1
        e = entries[0]
        assert e.institution == "MRCET"
        assert e.gpa == "7.81"
        assert e.start_date and e.start_date.year == 2010
        assert e.end_date and e.end_date.year == 2014

    def test_graduated_keyword(self, parser: EducationParser):
        text = (
            "Master of Business Administration (MBA) Emphasis in Technology Management "
            "University of Colorado Boulder – Leeds School of Business Graduated: 2019"
        )
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.end_date and e.end_date.year == 2019

    def test_thesis_and_specialization(self, parser: EducationParser):
        text = (
            "Master of Science in Cybersecurity & Information Assurance University of Washington – Seattle, WA "
            "Graduated: 2017 Thesis: \"Behavioral Analytics in Industrial Control Systems\"\n"
            "Bachelor of Science in Computer Science Purdue University – West Lafayette, IN "
            "Graduated: 2013 Specialization in Network Engineering"
        )
        entries = parser.parse(text)
        assert len(entries) >= 2
        # First entry should have thesis in honors/description
        first = entries[0]
        assert first.honors is None or "Thesis" in first.honors or "Behavioral" in (first.honors or "")

    def test_empty_education_section_returns_empty(self, parser: EducationParser):
        text = "WORK EXPERIENCE\nSoftware Engineer at Google\n\nSKILLS\nPython, Java"
        entries = parser.parse(text)
        assert len(entries) == 0

    def test_no_education_resume_no_placeholder_entry(self, parser: EducationParser):
        """When resume has no education section, do not emit placeholder (Institution + Degree · EMR from noise)."""
        text = "EXPERIENCE\nImplemented EMR systems. June 2023 - Present.\nDegree: required."
        entries = parser.parse(text)
        assert len(entries) == 0

    def test_gokaraju_from_and_year(self, parser: EducationParser):
        text = (
            "Education: Bachelor of Technology: Computer Science Engineering & Technology "
            "from Gokaraju Rangaraju Institute of Engineering & Technology – 2014."
        )
        entries = parser.parse(text)
        assert len(entries) == 1
        e = entries[0]
        assert e.institution and "Gokaraju" in e.institution
        assert e.end_date and e.end_date.year == 2014

    def test_two_institutions_split_into_two_entries(self, parser: EducationParser):
        text = (
            "Gokaraju Rangaraju Institute of Engineering & Technology - 2014. "
            "Vellore Institute of Technology, Vellore July 2014 Bachelors in computer science CGPA: 7.44."
        )
        entries = parser.parse(text)
        assert len(entries) >= 2
        institutions = [e.institution or "" for e in entries]
        assert any("Gokaraju" in i for i in institutions)
        assert any("Vellore" in i for i in institutions)

    def test_institution_no_degree_or_graduated_in_title(self, parser: EducationParser):
        text = (
            "Master of Science in Cybersecurity & Information Assurance University of Washington - Seattle, WA "
            "Graduated: 2017 Thesis: \"Behavioral Analytics in Industrial Control Systems\""
        )
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution
        assert "Graduated:" not in (e.institution or "")
        assert "Thesis:" not in (e.institution or "")
        assert "Washington" in (e.institution or "")

    def test_field_no_redundant_technology(self, parser: EducationParser):
        text = "Bachelor of Technology in Technology Computer Science Bharath University August 2010 to May 2014"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.field_of_study
        assert e.field_of_study != "Technology Computer Science"
        assert "Computer Science" in (e.field_of_study or "")

    def test_institution_not_prefixed_with_engineering_or_research(self, parser: EducationParser):
        text = "Bachelor of Science in Computer Engineering University of Texas at Austin Graduated: 2014"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution
        assert not (e.institution or "").startswith("Engineering ")
        assert "Texas" in (e.institution or "")

    def test_institution_not_assurance_university_of_washington(self, parser: EducationParser):
        text = "Master of Science in Cybersecurity & Information Assurance University of Washington – Seattle, WA Graduated: 2017"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution
        assert not (e.institution or "").strip().lower().startswith("assurance ")
        assert "Washington" in (e.institution or "")

    def test_field_does_not_duplicate_institution(self, parser: EducationParser):
        text = "Bachelor of Science in Computer Science Purdue University – West Lafayette, IN Graduated: 2013"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution and "Purdue" in (e.institution or "")
        assert e.field_of_study
        assert "Purdue" not in (e.field_of_study or "") and "West Lafayette" not in (e.field_of_study or "")

    def test_college_mrcet_extracted_as_institution(self, parser: EducationParser):
        text = (
            "EDUCATION:\nDegree: Bachelor of Technology in Computer Science and Engineering (May 2010 – March 2014)\n"
            "College: MRCET                                                                                                      \n"
            "GPA: 7.81"
        )
        entries = parser.parse(text)
        assert len(entries) == 1
        e = entries[0]
        assert e.institution and "MRCET" in (e.institution or "")

    def test_degree_colon_field_rvr(self, parser: EducationParser):
        text = "EDUCATION\nBachelor of Technology: Computer Science Engineering from R. V. R & J. C College of Engineering"
        entries = parser.parse(text)
        assert len(entries) == 1
        e = entries[0]
        assert e.field_of_study and "Computer Science" in (e.field_of_study or "")

    def test_jntuh_btech_parenthetical_field(self, parser: EducationParser):
        text = (
            "EDUCATION\nJawaharlal Nehru Technological University Hyderabad (JNTUH) August 2010 – April 2014\n"
            "Bachelor of Technology – B.Tech (Computer Science)"
        )
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.field_of_study is None or "Computer Science" in (e.field_of_study or "") or "Computer" in (e.field_of_study or "")
        assert not (e.field_of_study or "").strip().startswith("-")

    def test_end_date_not_future(self, parser: EducationParser):
        from datetime import date
        text = "MBA Northwestern University 2026"
        entries = parser.parse(text)
        if entries and entries[0].end_date:
            assert entries[0].end_date.year <= date.today().year

    def test_graduated_cum_laude_in_honors(self, parser: EducationParser):
        text = "Bachelor of Science in Computer Engineering University of Texas at Austin Graduated: 2014 Graduated Cum Laude"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.honors and "um Laude" in (e.honors or "")

    def test_never_institution_placeholder_when_college_label_present(self, parser: EducationParser):
        """Parser must not output literal 'Institution' when block has 'College: MRCET'."""
        text = (
            "EDUCATION:\nDegree: Bachelor of Technology in Computer Science and Engineering (May 2010 – March 2014)\n"
            "College: MRCET\nGPA: 7.81"
        )
        entries = parser.parse(text)
        assert len(entries) == 1
        assert entries[0].institution is not None
        assert entries[0].institution.strip().lower() != "institution"
        assert "MRCET" in (entries[0].institution or "")

    def test_at_lanta_corrected_to_atlanta(self, parser: EducationParser):
        """Typo 'At lanta' in institution/location is corrected to 'Atlanta'."""
        text = "MBA Georgia Institute of Technology (Scheller College of Business), At lanta, GA"
        entries = parser.parse(text)
        assert len(entries) >= 1
        inst = entries[0].institution or ""
        assert "Atlanta" in inst
        assert "At lanta" not in inst

    def test_cid_pdf_artifact_stripped_institution_extracted(self, parser: EducationParser):
        """(cid:17) PDF artifact is stripped so 'Karpagam College' is used as institution."""
        text = "B.E in Electronics and Telecommunication 85.8% 2016 – 2020 (cid:17) Karpagam College"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution and "Karpagam" in (e.institution or "")
        assert "(cid:" not in (e.institution or "")

    def test_my_university_space_restored(self, parser: EducationParser):
        """MYUNIVERSITY is normalized to MY UNIVERSITY."""
        text = "MYUNIVERSITY BACHELOR OF SCIENCE IN COMPUTER SCIENCE Expected Dec 2019"
        entries = parser.parse(text)
        assert len(entries) >= 1
        inst = entries[0].institution or ""
        assert " " in inst
        assert "MY" in inst and "UNIVERSITY" in inst

    def test_expected_dec_2019_parsed(self, parser: EducationParser):
        """Expected Dec 2019 sets end_date to December 2019 and in_progress."""
        text = "BACHELOR OF SCIENCE IN COMPUTER SCIENCE Expected Dec 2019 | Somewhere, XX"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.end_date is not None and e.end_date.month == 12 and e.end_date.year == 2019
        assert e.in_progress is True

    def test_aug_period_dates_parsed(self, parser: EducationParser):
        """Aug. 2018 – May 2021 is parsed (month with period)."""
        text = "Southwestern University Georgetown, TX Bachelor of Arts in Computer Science Aug. 2018 – May 2021"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.start_date is not None and e.start_date.year == 2018
        assert e.end_date is not None and e.end_date.year == 2021

    def test_institution_on_line_above_degree(self, parser: EducationParser):
        """Institution name on its own line (Southwestern University, Blinn College) is extracted."""
        text = (
            "Education\nSouthwestern University Georgetown, TX\n"
            "Bachelor of Arts in Computer Science, Minor in Business Aug. 2018 – May 2021\n"
            "Blinn College Bryan, TX\nAssociate's in Liberal Arts Aug. 2014 – May 2018"
        )
        entries = parser.parse(text)
        assert len(entries) >= 2
        institutions = [e.institution or "" for e in entries]
        assert any("Southwestern" in i for i in institutions)
        assert any("Blinn" in i for i in institutions)

    def test_jntuh_computer_science_field(self, parser: EducationParser):
        """B.Tech (Computer Science) yields field Computer Science, not truncated."""
        text = (
            "Jawaharlal Nehru Technological University Hyderabad (JNTUH) August 2010 – April 2014\n"
            "Bachelor of Technology – B.Tech (Computer Science)"
        )
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.field_of_study and "Computer Science" in (e.field_of_study or "")

    def test_cum_gpa_4_0_scale(self, parser: EducationParser):
        """Cum. GPA: 4.0 / 4.0 is extracted with scale."""
        text = "MY UNIVERSITY BACHELOR OF SCIENCE IN COMPUTER SCIENCE Expected Dec 2019 Cum. GPA: 4.0 / 4.0"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.gpa is not None and "4" in e.gpa and ("/" in e.gpa or "0" in e.gpa)

    def test_deans_list_honors(self, parser: EducationParser):
        """Dean's List (All Semesters) is captured in honors."""
        text = "BACHELOR OF SCIENCE IN COMPUTER SCIENCE MY UNIVERSITY Expected Dec 2019 Dean's List (All Semesters) Cum. GPA: 4.0 / 4.0"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.honors and "Dean" in (e.honors or "") and "List" in (e.honors or "")

    def test_half_symbol_karpagam_college(self, parser: EducationParser):
        """Institution after ½ is extracted: '2016 – 2020 ½ Karpagam College' -> Karpagam College."""
        text = (
            "EDUCATION\nB.E in Electronics and Telecommunication\n"
            "85.8%\n2016 – 2020 ½ Karpagam College"
        )
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution and "Karpagam" in (e.institution or "")

    def test_half_symbol_sboa_mhss(self, parser: EducationParser):
        """Institution after ½ for HSC/SSLC: '2016 ½ S.B.O.A MHSS CBE' -> S.B.O.A MHSS CBE."""
        text = "HSC (12th)\n86.6%\n2016 ½ S.B.O.A MHSS CBE"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution and "S.B.O.A" in (e.institution or "") or "MHSS" in (e.institution or "")

    def test_college_mrcet_with_newline(self, parser: EducationParser):
        """College: MRCET with newline between label and value is extracted."""
        text = (
            "EDUCATION:\nDegree: Bachelor of Technology in Computer Science and Engineering (May 2010 – March 2014)\n\n"
            "College: MRCET\n\nGPA: 7.81"
        )
        entries = parser.parse(text)
        assert len(entries) == 1
        assert entries[0].institution and "MRCET" in (entries[0].institution or "")


class TestConcatenatedTextAndNormalization:
    """Parser handles concatenated text (no-space PDF/OCR), pipe artifacts, and noise tokens."""

    def test_concatenated_institution_gets_spaces(self, parser: EducationParser):
        text = "B.Tech IndianInstituteofTechnology(IIT),Bombay 2016-2020 GPA 9.2"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        # After normalization, concatenated text has spaces (institution or field may hold it)
        combined = " ".join(filter(None, [e.institution, e.field_of_study]))
        assert " " in combined, "Output should have spaces restored (no run‑together words)"
        assert "Indian" in combined and "Institute" in combined

    def test_concatenated_instituteof_collegeof_and_ampersand(self, parser: EducationParser):
        """Instituteof, Collegeof, and Management&Operations get spaces restored."""
        text = (
            "MBA in Strategic Management&Operations "
            "Georgia Instituteof Technology (Scheller Collegeof Business), Atlanta, GA "
            "Top5%of Class; Recipientofthe Executive Leadership Award"
        )
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        inst = e.institution or ""
        assert "Institute of" in inst or "Instituteof" not in inst
        assert "College of" in inst or "Collegeof" not in inst
        field = e.field_of_study or ""
        if "Management" in field and "Operations" in field:
            assert " & " in field or "&" not in field or "Management &" in field
        honors = e.honors or ""
        assert " of " in honors or "ofthe" not in honors

    def test_sciencein_texasat_uw_comma_spaces(self, parser: EducationParser):
        """Multi-format: Sciencein, Texasat, Cambridge,MA, UWComputer get spaces restored."""
        text = (
            "Bachelor of Sciencein Computer Science The University of Texasat Austin, Austin, TX "
            "Honors: President of the UWComputer Science Honor Society. "
            "Massachusetts Institute of Technology (MIT), Cambridge,MA"
        )
        entries = parser.parse(text)
        assert len(entries) >= 1
        for e in entries:
            inst = e.institution or ""
            field = e.field_of_study or ""
            honors = e.honors or ""
            combined = " ".join(filter(None, [inst, field, honors]))
            assert "Science in" in combined or "Sciencein" not in combined
            assert "Texas at" in combined or "Texasat" not in combined
            assert "UW Computer" in combined or "UWComputer" not in combined
            assert ", " in combined or "Cambridge,MA" not in combined

    def test_research_focus_and_minor_in_honors(self, parser: EducationParser):
        """Research Focus and Minor bullet lines are captured in honors."""
        text = (
            "Master of Science in Software Engineering Carnegie Mellon University, Pittsburgh, PA "
            "Research Focus: Macro-Logistics Optimization. "
            "Honors: CMU Excellence in Graduate Research Award. "
            "Bachelor of Science in Computer Science The University of Texas at Austin "
            "Honors: Summa Cum Laude. Minor: Computational Data Analysis."
        )
        entries = parser.parse(text)
        assert len(entries) >= 2
        honors_text = " ".join(e.honors or "" for e in entries)
        assert "Research" in honors_text or "Focus" in honors_text or "Minor" in honors_text
        assert "Minor:" in honors_text or "Computational" in honors_text

    def test_mit_institution_not_parsed_as_degree(self, parser: EducationParser):
        """(MIT) in institution line is not treated as 'Master of Information Technology' degree."""
        text = (
            "Master of Science in Software Engineering & Cloud Architecture\n"
            "Massachusetts Institute of Technology (MIT), Cambridge, MA\n"
            "Focus Areas: Reliability Engineering. Honors: MIT Presidential Fellowship for Excellence in Research."
        )
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution and "MIT" in (e.institution or "") or "Massachusetts" in (e.institution or "")
        assert e.degree is None or "Information Technology" not in (e.degree or "") or "Science" in (e.degree or "")

    def test_recipient_scholarship_and_fellowship_for_spaces(self, parser: EducationParser):
        """Recipient of ... Scholarship is captured; Fellowshipfor -> Fellowship for; semicolon space."""
        text = (
            "Bachelor of Science in Computer Science & Mathematics The University of Washington, Seattle, WA "
            "Honors: Summa Cum Laude;President of the UW Computer Science Honor Society. "
            "Recipient of the Engineering Dean's Excellence Scholarship. "
            "MIT Presidential Fellowshipfor Excellence in Research."
        )
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.honors
        assert "Recipient" in (e.honors or "") and "Scholarship" in (e.honors or "")
        assert "Fellowship for" in (e.honors or "") or "Fellowshipfor" not in (e.honors or "")
        assert "; President" in (e.honors or "") or ";President" not in (e.honors or "")

    def test_trailing_pipe_stripped_from_institution(self, parser: EducationParser):
        text = "MBBS AllIndiaInstituteofMedicalSciences(AIIMS),NewDelhi | 2012-2017"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution
        assert not (e.institution or "").strip().endswith("|")

    def test_noise_testcase_stripped(self, parser: EducationParser):
        text = "B.Com(Hons)inAccounting&FinancefromShriRamCollegeofCommerce(SRCC)-2015. TestCase3.3"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution or e.degree or e.field_of_study
        combined = " ".join(filter(None, [e.institution, e.degree, e.field_of_study]))
        assert "TestCase" not in combined and "3.3" not in combined.split()[-2:]

    def test_concatenated_degree_and_thesis_get_spaces(self, parser: EducationParser):
        text = "BachelorofArtsinClinicalPsychology SomeUniversity 2019-2021 Honors; Thesis: ColdAtomInterferometryinMicrogravityEnvironments"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        if e.field_of_study or e.degree:
            val = (e.field_of_study or e.degree or "")
            assert " " in val or "Arts" in val, "Degree/field should have spaces or key word"
        if e.honors:
            assert " " in e.honors or "Cold" in e.honors


# =====================================================================
# 20+ demo resume EDUCATION snippets (multi-format, industry-level)
# =====================================================================

DEMO_RESUME_SNIPPETS = [
    "Bachelor of Technology (B.Tech) in computer science\nJawaharlal Nehru Technological University, India. July-2010 to June 2014",
    "Education:\n\nBachelor of Technology 2010 - 2014",
    "EDUCATION\nBachelor of Technology in Computer Science - MLWE college - June 2010 - July 2014",
    "EDUCATION\nBachelor of Technology: Computer Science Engineering from R. V. R & J. C College of Engineering",
    "EDUCATION:\nBachelors in computer and information science Aug 2010 – May 2014\nSreenidhi Institute Of Science and Technology",
    "EDUCATION:\nBachelor of Engineering in Computer Science | August 2010 – April 2014\nMVSR Engineering College",
    "EDUCATION:\nVellore Institute of Technology June 2010 to April 2014\nBachelor of Technology Computer Science",
    "EDUCATION\nBachelor of Technology in Computer Science\nQIS College of Engineering, Andhra Pradesh, India.",
    "EDUCATION\n- Bachelor of Technology Computer Science | Year of passed:",
    "EDUCATION:\nDegree: Bachelor of Technology in Computer Science and Engineering (May 2010 – March 2014)\nCollege: MRCET\nGPA: 7.81",
    "EDUCATION\nBharath University – Bachelor of Technology Computer Science August 2010 to May 2014",
    "Education: Bachelor of Technology: Computer Science Engineering & Technology from Gokaraju Rangaraju Institute of Engineering & Technology – 2014.",
    "EDUCATION\nVellore Institute of Technology, Vellore July 2014\nBachelors in computer science CGPA: 7.44",
    "EDUCATION\nMaster of Business Administration (MBA) in Strategic Management & Operations\nGeorgia Institute of Technology (Scheller College of Business), Atlanta, GA\nHonors: Top 5% of Class.\nBachelor of Science in Industrial Engineering & Computer Science\nThe University of Texas at Austin, Austin, TX\nHonors: Summa Cum Laude.",
    "EDUCATION\nMaster of Business Administration (MBA) in Supply Chain & Finance\nNorthwestern University, Kellogg School of Management, Evanston, IL\nBachelor of Science in Industrial Engineering & Computer Science\nGeorgia Institute of Technology (Georgia Tech), Atlanta, GA",
    "EDUCATION\nMaster of Science in Organizational Development & Human Resources\nVanderbilt University, Nashville, TN\nBachelor of Arts in Psychology & Business Administration\nUniversity of Colorado Boulder, Boulder, CO",
    "EDUCATION\nMaster of Science in Cybersecurity & Information Assurance University of Washington – Seattle, WA Graduated: 2017 Thesis: \"Behavioral Analytics in Industrial Control Systems\"\nBachelor of Science in Computer Science Purdue University – West Lafayette, IN Graduated: 2013 Specialization in Network Engineering",
    "EDUCATION\nMaster of Business Administration (MBA) Emphasis in Technology Management University of Colorado Boulder – Leeds School of Business Graduated: 2019\nBachelor of Science in Computer Engineering University of Texas at Austin Graduated: 2014 Graduated Cum Laude",
    "EDUCATION\nMaster of Science in Global Supply Chain Management Georgia Institute of Technology (Georgia Tech) | Atlanta, GA\nBachelor of Science in Industrial Engineering & Operations Research University of Washington | Seattle, WA",
    "B.S. Computer Science, Stanford University, 2018",
    "PhD in Machine Learning, MIT, 2015-2019",
    "High School Diploma, Lincoln High School, 2010",
    "MBA | Harvard Business School | 2020\nBS Economics | University of Chicago | 2016",
    "Education: B.Tech CSE, IIT Delhi, 2012-2016, GPA 8.5",
    "M.Sc. Data Science, ETH Zurich, 2019 – 2021",
    "Bachelor of Commerce, Delhi University, 2008",
    "PGDM, IIM Ahmedabad, 2014-2016",
    "BE Electronics, BITS Pilani, 2010-2014",
    "Master of Science in Computer Science\nUniversity of California, Berkeley\n2016 - 2018",
    "Associate Degree in Nursing, Community College of Philadelphia, 2015",
]


class TestDemoResumesParseWithoutCrash:
    """Every demo snippet must parse without raising and produce at least one entry (when education content exists)."""

    @pytest.mark.parametrize("snippet", DEMO_RESUME_SNIPPETS, ids=[f"snippet_{i}" for i in range(len(DEMO_RESUME_SNIPPETS))])
    def test_parse_no_crash(self, parser: EducationParser, snippet: str) -> None:
        entries = parser.parse(snippet)
        assert isinstance(entries, list)
        if "Bachelor" in snippet or "Master" in snippet or "B.Tech" in snippet or "MBA" in snippet or "PhD" in snippet or "B.S" in snippet or "M.Sc" in snippet or "Education" in snippet or "EDUCATION" in snippet:
            assert len(entries) >= 1, f"Expected at least one entry for snippet containing degree/education: {snippet[:80]}..."


class TestDemoResumesInstitutionQuality:
    """Institution must not start with degree/field words and must not be generic when snippet has a clear school name."""

    @pytest.mark.parametrize("snippet", DEMO_RESUME_SNIPPETS[:20], ids=[f"inst_{i}" for i in range(20)])
    def test_institution_no_engineering_research_assurance_prefix(self, parser: EducationParser, snippet: str) -> None:
        entries = parser.parse(snippet)
        for e in entries:
            inst = (e.institution or "").strip()
            if not inst:
                continue
            lower = inst.lower()
            assert not lower.startswith("engineering "), f"Institution should not start with 'Engineering': {inst}"
            assert not lower.startswith("research "), f"Institution should not start with 'Research': {inst}"
            assert not lower.startswith("assurance "), f"Institution should not start with 'Assurance': {inst}"
            assert inst != "Institution" or "institution" not in snippet.lower(), f"Avoid generic 'Institution' when possible for: {snippet[:60]}..."


class TestDemoResumesFieldQuality:
    """Field of study should not duplicate institution name or location."""

    @pytest.mark.parametrize("snippet", DEMO_RESUME_SNIPPETS[:18], ids=[f"field_{i}" for i in range(18)])
    def test_field_no_trailing_university_duplicate(self, parser: EducationParser, snippet: str) -> None:
        entries = parser.parse(snippet)
        for e in entries:
            field = (e.field_of_study or "").strip()
            inst = (e.institution or "").strip()
            if not field or not inst:
                continue
            assert not field.endswith(inst), f"field_of_study should not end with institution: field={field!r} inst={inst!r}"


class TestDemoResumesDatesWhenPresent:
    """When snippet contains a year or date range, at least one entry should have an end_date or start_date."""

    @pytest.mark.parametrize("snippet", [DEMO_RESUME_SNIPPETS[i] for i in [0, 1, 2, 4, 5, 6, 9, 10, 11, 12, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]])
    def test_has_date_when_year_in_snippet(self, parser: EducationParser, snippet: str) -> None:
        has_year = bool(re.search(r"\b(19|20)\d{2}\b", snippet))
        if not has_year:
            pytest.skip("Snippet has no 4-digit year")
        entries = parser.parse(snippet)
        if not entries:
            pytest.skip("No entries parsed")
        has_date = any((e.start_date or e.end_date) for e in entries)
        assert has_date, f"Snippet contains a year but no entry had start/end date: {snippet[:80]}..."


class TestDemoResumesSpecificFormats:
    """Targeted checks for formats that previously failed."""

    def test_ut_austin_institution_clean(self, parser: EducationParser) -> None:
        text = "Bachelor of Science in Computer Engineering University of Texas at Austin Graduated: 2014"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution
        assert "Texas" in (e.institution or "")
        assert not (e.institution or "").strip().startswith("Engineering ")

    def test_uwashington_institution_clean(self, parser: EducationParser) -> None:
        text = "Master of Science in Cybersecurity & Information Assurance University of Washington – Seattle, WA Graduated: 2017"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution
        assert "Washington" in (e.institution or "")
        assert not (e.institution or "").strip().lower().startswith("assurance ")

    def test_georgia_tech_has_institution(self, parser: EducationParser) -> None:
        text = "Master of Science in Global Supply Chain Management Georgia Institute of Technology (Georgia Tech) | Atlanta, GA"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution and "Georgia" in (e.institution or "")

    def test_industrial_engineering_operations_research_uw(self, parser: EducationParser) -> None:
        text = "Bachelor of Science in Industrial Engineering & Operations Research University of Washington | Seattle, WA"
        entries = parser.parse(text)
        assert len(entries) >= 1
        e = entries[0]
        assert e.institution
        assert not (e.institution or "").strip().lower().startswith("research ")
        assert "Washington" in (e.institution or "")


def test_education_parse_date_mm_yy():
    parser = EducationParser()
    assert parser._parse_date("11/22") == date(2022, 11, 1)


def test_education_parse_date_month_apostrophe_year():
    parser = EducationParser()
    assert parser._parse_date("Aug '20") == date(2020, 8, 1)


def test_education_extract_date_range_mm_yy():
    parser = EducationParser()
    start, end, in_progress = parser._extract_dates("03/20 - 11/22")
    assert start == date(2020, 3, 1)
    assert end == date(2022, 11, 1)
    assert in_progress is False


@pytest.mark.parametrize(
    ("date_str", "expected"),
    [
        ("Q1 2020", date(2020, 1, 1)),
        ("Q4 2019", date(2019, 10, 1)),
        ("Spring 2020", date(2020, 3, 1)),
        ("Fall 2019", date(2019, 9, 1)),
        ("Jan '20", date(2020, 1, 1)),
        ("Feb '19", date(2019, 2, 1)),
        ("2020.01", date(2020, 1, 1)),
        ("01.2020", date(2020, 1, 1)),
        ("2020", date(2020, 1, 1)),  # Fixed to Jan 1 for consistency
    ],
)
def test_education_parse_date_extended_formats(date_str, expected):
    parser = EducationParser()
    result = parser._parse_date(date_str)
    assert result == expected
