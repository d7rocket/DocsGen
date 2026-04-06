"""Markdown section detection and extraction for DocsGen skill.

Parses source Markdown files from pbi:docs output, detects ## headings,
maps them to known section categories via keyword matching, and returns
structured section content for document generation.
"""

import os
import re
import yaml


def _load_section_map(map_path: str | None = None) -> list[dict]:
    """Load the section heading map from YAML. Returns the list under 'sections' key."""
    if map_path is None:
        map_path = os.path.join(
            os.path.dirname(__file__), "..", "references", "section_heading_map.yaml"
        )
    with open(map_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["sections"]


def _is_in_code_block(lines: list[str], line_index: int) -> bool:
    """Check if a line is inside a fenced code block by counting ``` markers before it."""
    fence_count = 0
    for i in range(line_index):
        if lines[i].strip().startswith("```"):
            fence_count += 1
    return fence_count % 2 == 1


def _match_heading_to_section(heading_text: str, section_map: list[dict]) -> str | None:
    """Match a heading to a section ID via case-insensitive keyword substring matching.

    Returns the section id (e.g., 'overview') or None. First match wins.
    """
    lower_heading = heading_text.lower()
    for section in section_map:
        for keyword in section["keywords"]:
            if keyword.lower() in lower_heading:
                return section["id"]
    return None


def parse_markdown_sources(source_files: list[str], map_path: str | None = None) -> dict[str, dict]:
    """Parse source Markdown files and extract sections by heading keyword matching.

    Reads and concatenates all source files, scans for ## headings,
    maps them to section categories, and returns a dict keyed by section id.

    Args:
        source_files: List of paths to Markdown files to parse.
        map_path: Optional path to section_heading_map.yaml. Defaults to references/ dir.

    Returns:
        Dict keyed by section id, e.g.:
        {"overview": {"label": "Project Overview", "content": "..."}, ...}
        Sections with only whitespace content are excluded.
    """
    section_map = _load_section_map(map_path)

    # Build a lookup from section id to label
    label_lookup = {s["id"]: s["label"] for s in section_map}

    # Concatenate all source files
    all_lines: list[str] = []
    for file_path in source_files:
        with open(file_path, "r", encoding="utf-8") as f:
            all_lines.extend(f.readlines())
        all_lines.append("\n")  # separator between files

    heading_pattern = re.compile(r"^##\s+(.+)")

    # First pass: find all matched headings and their line positions
    matched_headings: list[tuple[int, str, str]] = []  # (line_index, section_id, label)
    for i, line in enumerate(all_lines):
        if _is_in_code_block(all_lines, i):
            continue
        match = heading_pattern.match(line.rstrip())
        if match:
            heading_text = match.group(1)
            section_id = _match_heading_to_section(heading_text, section_map)
            if section_id is not None:
                matched_headings.append((i, section_id, label_lookup[section_id]))

    # Second pass: extract content between headings
    result: dict[str, dict] = {}
    for idx, (line_num, section_id, label) in enumerate(matched_headings):
        # Content starts after the heading line
        start = line_num + 1
        # Content ends at the next matched heading or end of file
        if idx + 1 < len(matched_headings):
            end = matched_headings[idx + 1][0]
        else:
            end = len(all_lines)

        content_lines = all_lines[start:end]
        content = "".join(content_lines).strip()

        # Skip sections with no actual content (PARSE-03 / D-12)
        if not content:
            continue

        # If multiple headings match the same section id, concatenate
        if section_id in result:
            result[section_id]["content"] += "\n\n" + content
        else:
            result[section_id] = {"label": label, "content": content}

    return result
