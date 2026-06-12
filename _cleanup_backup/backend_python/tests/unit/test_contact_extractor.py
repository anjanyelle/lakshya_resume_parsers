from app.services.parser.contact_extractor import ContactExtractor


def test_extract_emails_and_primary():
    text = "Reach me at jane.doe@gmail.com or jane@company.com"
    extractor = ContactExtractor(default_region="US")
    emails = extractor.extract_emails(text)
    assert emails
    assert emails[0].email in {"jane.doe@gmail.com", "jane@company.com"}
    assert emails[0].is_primary is True


def test_extract_phones_normalizes_e164():
    text = "Call +1 (415) 555-1234 or 415-555-1234"
    extractor = ContactExtractor(default_region="US")
    phones = extractor.extract_phones(text)
    assert any(phone.phone.startswith("+1") for phone in phones)


def test_extract_urls_linkedin_github():
    text = "LinkedIn: linkedin.com/in/janedoe GitHub: https://github.com/janedoe"
    extractor = ContactExtractor(default_region="US")
    urls = extractor.extract_urls(text)
    assert urls.linkedin and "linkedin.com" in urls.linkedin
    assert urls.github and "github.com" in urls.github


def test_extract_location_city_state():
    text = "Jane Doe\nAustin, TX\nUnited States"
    extractor = ContactExtractor(default_region="US")
    location = extractor.extract_location(text)
    assert location.city == "Austin"
    assert location.state == "TX"


def test_extract_name_first_line_no_label():
    """Resume where line 1 is 'John Smith' (no 'Name:' label) returns 'John Smith'."""
    text = "John Smith\nSoftware Engineer\njohn@example.com"
    extractor = ContactExtractor(default_region="US")
    result = extractor.extract_name(text)
    assert result.name == "John Smith"


def test_extract_name_fallback():
    text = "Jane Doe\nSoftware Engineer\njane@example.com"
    extractor = ContactExtractor(default_region="US")
    name = extractor.extract_name(text)
    assert name.name == "Jane Doe"


def test_invalid_emails_ignored():
    text = "invalid-email@ and valid@example.com"
    extractor = ContactExtractor(default_region="US")
    emails = extractor.extract_emails(text)
    assert len(emails) == 1
    assert emails[0].email == "valid@example.com"
