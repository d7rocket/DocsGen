"""Pipeline entry point for DocsGen skill.

Wires together md_parser, content_generator, and docx_builder into a single
invocation. Reads a JSON config file and executes the full pipeline:
parse source Markdown -> generate section content -> build branded DOCX.

Usage:
    python generate.py <config.json>

All progress messages go to stderr. Only the final output path goes to stdout,
so SKILL.md can capture it cleanly.
"""

import sys
import os
import json
import time


def check_dependencies() -> bool:
    """Check that all required Python dependencies are importable.

    Per SCAF-04: verifies python-docx, Jinja2, and PyYAML are available.
    Prints specific install instructions to stderr for any missing package.

    Returns:
        True if all dependencies are present, False if any are missing.
    """
    deps = {
        "docx": "python-docx==1.2.0",
        "jinja2": "Jinja2",
        "yaml": "PyYAML",
    }
    all_ok = True
    for module_name, package_name in deps.items():
        try:
            __import__(module_name)
        except ImportError:
            print(
                f"Missing dependency: {module_name}. Install with: pip install {package_name}",
                file=sys.stderr,
            )
            all_ok = False
    # Playwright is required for Phase 2 PDF output (non-blocking for Phase 1 DOCX)
    try:
        __import__("playwright")
    except ImportError:
        print(
            "Note: playwright not installed. Required for PDF output (Phase 2). "
            "Install with: pip install playwright==1.58.0 && playwright install chromium",
            file=sys.stderr,
        )
    return all_ok


def main(config_path: str) -> None:
    """Execute the full DocsGen pipeline: parse -> generate content -> build DOCX.

    Args:
        config_path: Path to the JSON configuration file.

    Pipeline stages (per D-21):
        1. Parse source Markdown files into structured sections
        2. Generate professional prose for each section via LLM
        3. Build branded Word document from generated content
    """
    # Step 1: Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Add skill root to sys.path for imports
    skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if skill_root not in sys.path:
        sys.path.insert(0, skill_root)

    from scripts.utils import load_json_config, ensure_directory, validate_file_exists
    from scripts.md_parser import parse_markdown_sources
    from scripts.content_generator import generate_all_sections
    from scripts.docx_builder import build_docx

    # Step 2: Load config
    config = load_json_config(config_path)

    # Step 3: Validate file paths
    for source_file in config["source_files"]:
        validate_file_exists(source_file, "Source file")
    validate_file_exists(config["client_logo"], "Client logo")
    validate_file_exists(config["company_logo"], "Company logo")
    print("All input files validated.", file=sys.stderr)

    # Step 4: Ensure output directory
    ensure_directory(config["output_dir"])

    # Stage 1/3: Parse Markdown
    print("Stage 1/3: Parsing source Markdown...", file=sys.stderr)
    parsed = parse_markdown_sources(config["source_files"])
    print(f"  Found {len(parsed)} sections: {', '.join(parsed.keys())}", file=sys.stderr)

    if not parsed:
        print(
            "No sections detected in source files. Check that source Markdown "
            "contains ## headings matching known section categories.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Stage 2/3: Generate content
    print("Stage 2/3: Generating section content...", file=sys.stderr)
    start = time.time()
    sections = generate_all_sections(
        parsed,
        config["client_name"],
        config["report_name"],
        config["audience"],
    )
    elapsed = time.time() - start
    print(f"  Content generated in {elapsed:.1f}s", file=sys.stderr)

    # Stage 3/3: Build DOCX
    print("Stage 3/3: Building Word document...", file=sys.stderr)
    output_path = build_docx(sections, config)
    file_size = os.path.getsize(output_path)
    print(f"\nComplete! Output: {output_path} ({file_size:,} bytes)", file=sys.stderr)

    # Print output path to stdout (for SKILL.md to capture)
    print(output_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate.py <config.json>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
