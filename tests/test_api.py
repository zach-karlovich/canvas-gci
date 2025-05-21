import os
from unittest.mock import Mock

import pytest
import requests
from canvas_gci.api import (
    CanvasAPI,
    CanvasAPIError,
    CanvasAPINotFound,
    CanvasAPIUnauthorized,
)
from canvas_gci.models import CanvasModule
from dotenv import load_dotenv

# Load .env file for local testing with real credentials (for recording cassettes)
load_dotenv()

# Placeholder - replace with a real course ID for recording cassettes
VALID_COURSE_ID = os.getenv("PYTEST_VALID_COURSE_ID", "12345")
# Placeholder - replace with a real API root if not default Canvas cloud
API_ROOT = os.getenv("PYTEST_CANVAS_API_ROOT", "https://canvas.instructure.com/api/v1")


@pytest.fixture
def api_client() -> CanvasAPI:
    return CanvasAPI(api_root=API_ROOT)


@pytest.mark.vcr
def test_get_modules_happy_path(api_client: CanvasAPI) -> None:
    """Test fetching modules for a valid course ID."""
    # Ensure PYTEST_VALID_COURSE_ID is set in your .env for recording
    modules = api_client.get_modules(int(VALID_COURSE_ID))
    assert modules is not None
    assert isinstance(modules, list)
    if modules:  # If the course has modules
        assert isinstance(modules[0], CanvasModule)
        assert hasattr(modules[0], "id")
        assert hasattr(modules[0], "name")
        assert hasattr(modules[0], "position")
    # Add more specific assertions based on expected data for your test course


@pytest.mark.vcr
def test_get_modules_not_found(api_client: CanvasAPI) -> None:
    """Test fetching modules for a non-existent course ID."""
    with pytest.raises(CanvasAPINotFound):
        api_client.get_modules(999999999)  # A very unlikely course ID


@pytest.mark.vcr
def test_get_modules_unauthorized(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test fetching modules with an invalid token."""
    # Temporarily set an invalid token
    monkeypatch.setenv("CANVAS_TOKEN", "INVALID_TOKEN_FOR_TESTING")
    # Create a new API client that will pick up the invalid token
    # This is important because the api_client fixture might have
    # already cached the original token or its session might have been
    # created with the valid one. Forcing re-initialization ensures
    # the new (invalid) token is used.
    unauth_api_client = CanvasAPI(api_root=API_ROOT)
    with pytest.raises(CanvasAPIUnauthorized):
        unauth_api_client.get_modules(
            int(VALID_COURSE_ID)
        )  # Use a valid course ID, as the error is auth, not not-found


def test_get_modules_server_error_retry(
    api_client: CanvasAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test server error and retry logic."""
    mock_response = Mock(
        status_code=500,
        headers={},
        json=lambda: {"error": "server error"},  # Mock json() method if called
    )
    mock_response.raise_for_status = Mock(
        side_effect=requests.exceptions.HTTPError("500 Server Error")
    )

    # Mock session.get to return the server error response multiple times
    # then optionally a success, or just keep failing to test exhaustion.
    # For simplicity, we'll just make it always return 500 here.
    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr(api_client.session, "get", mock_get)

    with pytest.raises(CanvasAPIError) as excinfo:
        api_client.get_modules(int(VALID_COURSE_ID))

    # Assert that the request was tried multiple times (initial + 3 retries = 4 calls)
    assert mock_get.call_count == 4
    assert "HTTP error: 500 Server Error" in str(excinfo.value)


# Test for general CanvasAPIError for other request exceptions (e.g. network)
# This is harder to test with VCR directly without more complex request
# matching or custom VCR logic. A unit test mocking session.get to raise
# requests.RequestException would be better.


def test_get_modules_network_error(
    api_client: CanvasAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test a generic network error during API call."""
    mock_get = Mock(
        side_effect=requests.exceptions.ConnectionError("Fake connection error")
    )
    monkeypatch.setattr(api_client.session, "get", mock_get)

    with pytest.raises(CanvasAPIError) as excinfo:
        api_client.get_modules(int(VALID_COURSE_ID))

    assert "Network or HTTP error: Fake connection error" in str(excinfo.value)
    # The request should be tried only once if it's a connection error
    # before raising RequestException
    assert mock_get.call_count == 1


# More tests to come for Server Error, etc.
