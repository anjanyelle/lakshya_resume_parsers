from datetime import date

from app.services.parser.education_parser import EducationParser


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
