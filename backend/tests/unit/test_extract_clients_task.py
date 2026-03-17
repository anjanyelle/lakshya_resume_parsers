from app.workers.extract_clients_task import _extract_all_clients, _extract_first_client


def test_extract_all_clients_multiple_in_description():
    """Description with 'Client: Acme Corp, Client: Beta Inc' yields both in results."""
    text = "Client: Acme Corp, Client: Beta Inc"
    results = _extract_all_clients(text)
    names = [name for name, _ in results]
    assert "Acme Corp" in names
    assert "Beta Inc" in names


def test_extract_client_case_insensitive():
    result = _extract_first_client("client: microsoft")
    assert result is not None
    assert result[0] == "Microsoft"
    assert result[1] in ("high", "medium")


def test_extract_client_working_for():
    result = _extract_first_client("working for acme")
    assert result is not None
    assert result[0] == "Acme"
    assert result[1] in ("high", "medium")
