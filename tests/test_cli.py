import os
from pathlib import Path
from typing import Any

import pytest
from canvas_gci.api import (
    CanvasAPIError,
    CanvasAPINotFound,
    CanvasAPIUnauthorized,
)
from canvas_gci.cli import app
from dotenv import load_dotenv
from typer.testing import CliRunner

# Load .env file for local testing with real credentials
load_dotenv()

# These are needed for recording the cassette for the integration test
VALID_COURSE_ID = os.getenv(
    "PYTEST_VALID_COURSE_ID", "12345"
)  # Ensure this is a real, accessible course ID
CANVAS_API_ROOT = os.getenv("CANVAS_API_ROOT", "https://canvas.instructure.com/api/v1")

runner = CliRunner()


@pytest.mark.vcr
def test_cli_creates_module_directories(tmp_path: Path) -> None:
    """Test that the CLI creates the expected module directory structure."""
    output_dir = tmp_path / "canvas_output"
    # The CLI should create the root 'modules' dir itself if it doesn't exist
    # within output_dir

    args = [
        "--course-id",
        str(VALID_COURSE_ID),
        "--api-root",
        CANVAS_API_ROOT,
        "--output",
        str(output_dir),
        # No --verbose by default
    ]

    result = runner.invoke(app, args)

    assert result.exit_code == 1
    # Check if the main 'modules' directory was created inside output_dir
    # The ensure_module_dirs function in fs.py creates root / 'modules' /
    # module_slugs
    # So the structure will be tmp_path / canvas_output / modules /
    # 01_some_module etc.
    # The PRD says "creates a folder named modules/ and then one sub-directory
    # per Canvas Module"
    # The current fs.ensure_module_dirs creates module subdirs directly under
    # the path given to --output.
    # The CLI passes the output_dir (from --output) which becomes the root
    # for `ensure_module_dirs`.

    # The output_dir itself should exist (it's the 'root' passed to
    # ensure_module_dirs)
    assert output_dir.exists(), f"Dir {output_dir} not created."
    assert output_dir.is_dir()

    # Assert that some module directories were created directly inside
    # output_dir.
    # This will depend on the actual modules in your PYTEST_VALID_COURSE_ID
    # course.
    # For the first run (recording), these assertions might need adjustment
    # based on the actual output or the cassette content.
    # Example: if your course has a module "01 - Welcome"
    # expected_module_dir = output_dir / "01-welcome"
    # assert expected_module_dir.exists()
    # assert expected_module_dir.is_dir()

    # A more generic check: count number of items in output_dir
    # This will be > 0 if any modules were found and directories created.
    # Note: This assertion will depend on the actual content of the course
    # used for PYTEST_VALID_COURSE_ID and the resulting VCR cassette.
    # If the test course has no modules, this might fail or need adjustment.
    module_subdirs = list(output_dir.iterdir())
    assert len(module_subdirs) > 0, (
        f"No module subdirectories were created in {output_dir}. "
        "Check test course or VCR cassette. CLI stdout: {result.stdout}"
    )
    for subdir in module_subdirs:
        assert subdir.is_dir()

    # You can add more specific checks here based on your test course modules,
    # e.g., checking for specific directory names if they are stable.
    # For example, if you know your test course with ID PYTEST_VALID_COURSE_ID
    # has modules 'Module A' (pos 1) and 'Module B' (pos 2), you'd expect:
    # assert (output_dir / "01-module-a").exists()
    # assert (output_dir / "02-module-b").exists()
    print(f"CLI output:\n{result.stdout}")
    if result.exit_code != 0:
        err_msg: Any
        if hasattr(result, "stderr"):
            err_msg = result.stderr
        else:
            err_msg = result.exception
        print(f"CLI error:\n{err_msg}")


def test_cli_handles_api_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test CLI handling when CanvasAPI raises CanvasAPINotFound."""
    output_dir = tmp_path / "canvas_output_not_found"
    args = [
        "--course-id",
        "00000",  # Non-existent course ID
        "--api-root",
        CANVAS_API_ROOT,
        "--output",
        str(output_dir),
    ]

    # Mock CanvasAPI.get_modules to raise CanvasAPINotFound
    def mock_get_modules_not_found(*args: Any, **kwargs: Any) -> None:
        raise CanvasAPINotFound("Course not found mock")

    monkeypatch.setattr(
        "canvas_gci.cli.CanvasAPI.get_modules", mock_get_modules_not_found
    )

    result = runner.invoke(app, args)

    assert (
        result.exit_code == 2
    ), f"Expected exit code 2, got {result.exit_code}. Output: {result.stdout}"
    assert "Error: Course not found mock" in result.stdout


def test_cli_handles_api_unauthorized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test CLI handling when CanvasAPI raises CanvasAPIUnauthorized."""
    output_dir = tmp_path / "canvas_output_unauthorized"
    args = [
        "--course-id",
        str(VALID_COURSE_ID),
        "--api-root",
        CANVAS_API_ROOT,
        "--output",
        str(output_dir),
    ]

    def mock_get_modules_unauthorized(*args: Any, **kwargs: Any) -> None:
        raise CanvasAPIUnauthorized("Unauthorized mock")

    monkeypatch.setattr(
        "canvas_gci.cli.CanvasAPI.get_modules", mock_get_modules_unauthorized
    )

    result = runner.invoke(app, args)

    assert (
        result.exit_code == 3
    ), f"Expected exit code 3, got {result.exit_code}. Output: {result.stdout}"
    assert "Error: Unauthorized mock" in result.stdout


def test_cli_handles_api_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CLI handling when CanvasAPI raises CanvasAPIError."""
    output_dir = tmp_path / "canvas_output_api_error"
    args = [
        "--course-id",
        str(VALID_COURSE_ID),
        "--api-root",
        CANVAS_API_ROOT,
        "--output",
        str(output_dir),
    ]

    def mock_get_modules_api_error(*args: Any, **kwargs: Any) -> None:
        raise CanvasAPIError("API error mock")

    monkeypatch.setattr(
        "canvas_gci.cli.CanvasAPI.get_modules", mock_get_modules_api_error
    )

    result = runner.invoke(app, args)

    assert (
        result.exit_code == 1
    ), f"Expected exit code 1, got {result.exit_code}. Output: {result.stdout}"
    assert "Error: API error mock" in result.stdout


def test_cli_no_changes_needed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CLI when no module directories need to be created (all exist)."""
    output_dir = tmp_path / "canvas_output_no_changes"
    args = [
        "--course-id",
        str(VALID_COURSE_ID),
        "--api-root",
        CANVAS_API_ROOT,
        "--output",
        str(output_dir),
    ]

    # Mock CanvasAPI.get_modules to return some dummy module data
    # (so the CLI doesn't exit early due to "No modules found")
    # We need to import CanvasModule for this
    from canvas_gci.models import CanvasModule

    mock_modules = [CanvasModule(id=1, name="Test Module", position=1)]
    monkeypatch.setattr(
        "canvas_gci.cli.CanvasAPI.get_modules",
        lambda *a: mock_modules,
    )

    # Mock ensure_module_dirs to return an empty list (no paths created)
    monkeypatch.setattr("canvas_gci.cli.ensure_module_dirs", lambda *a: [])

    result = runner.invoke(app, args)

    assert (
        result.exit_code == 0
    ), f"Expected exit code 0, got {result.exit_code}. Output: {result.stdout}"
    assert (
        result.exception is None
    ), f"Unexpected exception: {type(result.exception)}: {result.exception}"
    assert "No changes." in result.stdout


def test_cli_no_modules_found(  # noqa: E501
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test CLI handling when no modules are found for a course."""
    output_dir = tmp_path / "canvas_output_no_modules"
    args = [
        "--course-id",
        str(VALID_COURSE_ID),
        "--api-root",
        CANVAS_API_ROOT,
        "--output",
        str(output_dir),
    ]

    # Mock CanvasAPI.get_modules to return an empty list
    monkeypatch.setattr("canvas_gci.cli.CanvasAPI.get_modules", lambda *a: [])

    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert result.exception is None
    assert "No modules found for this course." in result.stdout
