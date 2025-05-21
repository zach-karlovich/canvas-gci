import tempfile
from pathlib import Path

import pytest
from canvas_gci.fs import ensure_module_dirs, slugify
from canvas_gci.models import CanvasModule


def test_slugify_basic() -> None:
    assert slugify("Introduction - Linear Regression") == (
        "introduction-linear-regression"
    )
    assert slugify("Week 03: k-NN & SVM") == "week-03-k-nn-svm"
    assert slugify("  Spaces  ") == "spaces"
    assert slugify("Symbols!@#%$") == "symbols"
    assert slugify("A" * 100) == "a" * 60


def test_slugify_strip_and_collapse() -> None:
    assert slugify("--foo--bar--") == "foo-bar"
    assert slugify("foo   bar") == "foo-bar"
    assert slugify("foo---bar") == "foo-bar"
    assert slugify("foo_bar:baz") == "foo-bar-baz"


def test_ensure_module_dirs_idempotent_and_collision() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        modules = [
            CanvasModule(id=1, name="Intro", position=1),
            CanvasModule(id=2, name="Intro", position=2),
            CanvasModule(id=3, name="Intro!", position=3),
        ]
        paths1 = ensure_module_dirs(root, modules)
        paths2 = ensure_module_dirs(root, modules)
        # Should not create duplicates
        assert set(paths1) == set(paths2)
        # All slugs should be unique and match the expected pattern
        slugs = [p.name for p in paths1]
        assert len(set(slugs)) == len(slugs)
        assert sorted(slugs) == ["01-intro", "02-intro", "03-intro"]


def test_ensure_module_dirs_permission_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate permission error by making root unwritable
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "readonly"
        root.mkdir()
        root.chmod(0o400)
        modules = [CanvasModule(id=1, name="Test", position=1)]
        try:
            with pytest.raises(PermissionError):
                ensure_module_dirs(root, modules)
        finally:
            # Restore permissions so temp dir can be cleaned up
            root.chmod(0o700)
