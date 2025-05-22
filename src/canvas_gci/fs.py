import re
from pathlib import Path
from typing import List

from .models import CanvasModule

__all__ = ["slugify", "ensure_module_dirs"]


def slugify(name: str) -> str:
    """
    Convert a name string to a kebab-case, ASCII-safe slug.
    If "module <number>" is found in the name, the slug will be in the format
    'm<number>-<slugified-title>', where <title> is the part of the name
    after "module <number>". Otherwise, the entire name (after initial
    prefix stripping) is slugified.

    Processing steps:
    1. Removes leading "##-" prefixes (e.g., "01-", "12-") from the input name.
    2. Converts the processed name to lowercase.
    3. Attempts to find "module" (case-insensitive) and a subsequent number
       (e.g., "Module 123", "module-42").
       - If this "module <number>" pattern is found:
         a. The extracted number forms an 'm<number>' prefix (e.g., "m123").
         b. The part of the name string that appears *after* the full
            "module <number>" pattern is taken as the base for the title slug.
         c. This title base is then slugified:
            - Any run of non-alphanumeric characters is replaced with a single
              hyphen '-'.
            - Leading and trailing hyphens are stripped.
         d. The final slug is 'm<number>-<slugified-title>' or 'm<number>'
            if the slugified title part is empty.
       - If the "module <number>" pattern is NOT found:
         a. The entire processed name (from step 1, lowercased) is taken as
            the base for slugification.
         b. This base is slugified as described above (non-alphanumerics to
            hyphens, then stripped).
    4. The resulting slug is truncated to a maximum of 60 characters.
    """
    processed_name = name

    # Step 1: Remove leading "##-" prefixes
    processed_name = re.sub(r"^\d+-", "", processed_name)

    name_lower = processed_name.lower()

    # Step 3: Attempt to find "module" and extract module number & title base
    module_slug_prefix = ""
    # Default to using the full lowercased name (after prefix stripping)
    # for slugification if module pattern is not found or is incomplete.
    text_to_slugify = name_lower

    module_keyword_match = re.search(r"module", name_lower)
    if module_keyword_match:
        # Search for "module[\\s_-]*(\\d+)" starting from where "module"
        # was found.
        search_start_index = module_keyword_match.start()
        search_string_for_num_pattern = name_lower[search_start_index:]
        # This regex captures the number after "module" and optional
        # separators.
        module_num_pattern_regex = r"module[\s_-]*(\d+)"
        module_pattern_match = re.search(
            module_num_pattern_regex, search_string_for_num_pattern
        )

        if module_pattern_match:
            # "module <number>" pattern was successfully matched.
            module_number = module_pattern_match.group(1)
            module_slug_prefix = f"m{int(module_number)}"

            # The text to slugify is what comes *after* the "module <number>"
            # match. module_pattern_match.end() is an index relative to
            # search_string_for_num_pattern.
            # Adjust by module_keyword_match.start() to get the correct
            # slice from the original name_lower.
            title_start_offset = module_pattern_match.end()
            title_start_idx = search_start_index + title_start_offset
            text_to_slugify = name_lower[title_start_idx:]
        # If module_pattern_match is None, "module" was found but not the
        # "module <number>" pattern. In this case, text_to_slugify remains
        # name_lower (as initialized), and module_slug_prefix remains "".
        # This effectively means we slugify the whole name_lower.

    # Slugify the determined text_to_slugify
    slugified_core_part = ""
    # Only process if there's non-whitespace content
    if text_to_slugify.strip():
        # Replace non-alphanumerics with a single dash
        temp_slug = re.sub(r"[^a-zA-Z0-9]+", "-", text_to_slugify.strip())
        # Strip leading/trailing hyphens from this part
        slugified_core_part = temp_slug.strip("-")

    # Construct final slug
    if module_slug_prefix:  # "module <number>" was found and prefix generated
        if slugified_core_part:
            final_slug = f"{module_slug_prefix}-{slugified_core_part}"
        else:
            # e.g., "m123" if title part was empty
            final_slug = module_slug_prefix
    else:
        # "module <number>" pattern was NOT found (or "module" keyword
        # itself was not found).
        # Return empty string to signal that no directory should be created.
        return ""

    # Step 4: Truncate to 60 chars
    final_slug = final_slug[:60]

    return final_slug


def ensure_module_dirs(root: Path, modules: List[CanvasModule]) -> List[Path]:
    """
    Create module directories under root, using slugified names.
    Only creates directories for modules whose names result in a valid
    (non-empty) slug (e.g., containing "module <number>").
    Idempotent: does not overwrite existing dirs. Handles slug collisions.
    Returns a list of created/existing paths.
    """
    root.mkdir(parents=True, exist_ok=True)
    created_paths = []
    used: set[str] = set()
    for module in modules:
        base_slug = slugify(module.name)

        # Skip if slug is empty (e.g., item is not a typical module,
        # like "Course Information").
        if not base_slug:
            continue

        slug = base_slug
        i = 2
        while True:
            # Directory name is now just the slug
            # (or slug-i for collision handling)
            dir_name = slug
            path = root / dir_name
            # If the directory exists, treat it as idempotent and use it
            if dir_name not in used and path.exists():
                break
            # If new and not used in this run, use it
            if dir_name not in used and not path.exists():
                break
            slug = f"{base_slug}-{i}"
            i += 1
        used.add(dir_name)
        path.mkdir(exist_ok=True)
        created_paths.append(path)
    return created_paths
