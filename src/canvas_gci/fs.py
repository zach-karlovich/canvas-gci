import re
from pathlib import Path
from typing import List

from .models import CanvasModule

__all__ = ["slugify", "ensure_module_dirs"]


def slugify(name: str) -> str:
    """
    Convert a string to a kebab-case, ASCII-safe slug:
    - Lowercase
    - Replace any run of non-alphanumerics with one '-'
    - Strip leading/trailing '-'
    - Truncate to 60 chars
    """
    # Replace any run of non-alphanumerics with a single dash
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower())
    slug = slug.strip("-")
    slug = slug[:60]
    return slug


def ensure_module_dirs(root: Path, modules: List[CanvasModule]) -> List[Path]:
    """
    Create module directories under root, using slugified names and position.
    Idempotent: does not overwrite existing dirs. Handles slug collisions.
    Returns a list of created/existing paths.
    """
    root.mkdir(parents=True, exist_ok=True)
    created_paths = []
    used = set()
    for module in modules:
        base_slug = slugify(module.name)
        slug = base_slug
        i = 2
        while True:
            dir_name = f"{module.position:02d}-{slug}"
            path = root / dir_name
            # If the directory exists, treat it as idempotent and use it
            if dir_name not in used and path.exists():
                break
            # If the directory does not exist and is not used in this run, use it
            if dir_name not in used and not path.exists():
                break
            slug = f"{base_slug}-{i}"
            i += 1
        used.add(dir_name)
        path.mkdir(exist_ok=True)
        created_paths.append(path)
    return created_paths
