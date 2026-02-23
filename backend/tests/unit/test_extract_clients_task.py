from app.workers.extract_clients_task import _extract_first_client


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
