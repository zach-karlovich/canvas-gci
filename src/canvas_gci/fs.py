import re
from pathlib import Path
from typing import List

from .models import CanvasModule

__all__ = ["slugify", "ensure_module_dirs"]


def slugify(name: str) -> str:
    """
    Convert a module name string to a kebab-case, ASCII-safe slug.
    The slug will be in the format 'm<number>-<slugified-title>'.

    Processing steps:
    1. Removes leading "##-" prefixes (e.g., "01-", "12-").
    2. Converts the name to lowercase for processing.
    3. If "module" (case-insensitive) is not found in the name,
       returns an empty string.
    4. Extracts the first number following "module" (e.g., from "Module 123").
       This number forms the 'm<number>' prefix (e.g., "m123").
    5. The part of the name string that appears *after* the "module <number>"
       pattern is taken as the base for the title.
    6. This title base is then slugified:
        - Any run of non-alphanumeric characters is replaced with a single
          hyphen '-'.
        - Leading and trailing hyphens are stripped from this slugified
          title part.
    7. The final slug is constructed as 'm<number>-<slugified-title>'.
       Else, the slug is 'm<number>'.  # noqa: E501
    8. The resulting slug is truncated to a maximum of 60 characters.
    """
    processed_name = name

    # Step 1: Remove leading "##-" prefixes (e.g., "01-", "12-").
    # This regex matches leading digits and a hyphen.
    processed_name = re.sub(r"^\d+-", "", processed_name)

    name_lower = processed_name.lower()

    # Step 3: Check for "module" (Step 2 is implicit in name_lower).
    # Search for "module" case-insensitively by operating on name_lower.
    module_keyword_match = re.search(r"module", name_lower)
    if not module_keyword_match:
        return ""  # Drop if "module" is not found

    # Step 4: Extract module number.
    # Search in the part of the string starting from where "module" was found.
    search_string_for_num = name_lower[module_keyword_match.start() :]
    module_num_pattern = r"module[\s_-]*(\d+)"
    module_pattern_match = re.search(module_num_pattern, search_string_for_num)

    if not module_pattern_match:
        # "module" was found, but not in the "module <number>" format
        # we expect.
        return ""

    module_number = module_pattern_match.group(1)
    module_slug_prefix = f"m{int(module_number)}"

    # Step 5: Get the part of the name *after* "module <number>" pattern.
    # module_pattern_match.end() is an index relative to search_string_for_num.
    # Adjust by adding module_keyword_match.start() to get the index
    # in original name_lower.
    title_start_idx = module_keyword_match.start() + module_pattern_match.end()
    title_text = name_lower[title_start_idx:]

    # Step 6: Slugify the title text
    slugified_title_part = ""
    if title_text.strip():  # Only process if there's non-whitespace content
        # Replace non-alphanumerics with a single dash
        temp_title_slug = re.sub(r"[^a-zA-Z0-9]+", "-", title_text.strip())
        # Strip leading/trailing hyphens from this part
        slugified_title_part = temp_title_slug.strip("-")

    # Step 7: Construct final slug
    if slugified_title_part:
        final_slug = f"{module_slug_prefix}-{slugified_title_part}"
    else:
        final_slug = module_slug_prefix

    # Step 8: Truncate to 60 chars
    final_slug = final_slug[:60]

    return final_slug


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
            # If the directory does not exist and is not used in this run, use it  # noqa: E501
            if dir_name not in used and not path.exists():
                break
            slug = f"{base_slug}-{i}"
            i += 1
        used.add(dir_name)
        path.mkdir(exist_ok=True)
        created_paths.append(path)
    return created_paths
