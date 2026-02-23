from datetime import date

import pytest

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
        ("2020", date(2020, 2, 1)),  # dateparser returns Feb 1 for bare year
    ],
)
def test_education_parse_date_extended_formats(date_str, expected):
    parser = EducationParser()
    result = parser._parse_date(date_str)
    assert result == expected
