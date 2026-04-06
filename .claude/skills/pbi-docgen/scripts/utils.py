"""Shared utilities for DocsGen skill: color parsing, file validation, path resolution."""

import os
import json
import sys


def parse_hex_color(hex_str: str) -> tuple[int, int, int]:
    """Parse a hex color string (with or without '#') and return an (r, g, b) tuple."""
    cleaned = hex_str.strip().lstrip("#")
    if len(cleaned) != 6:
        raise ValueError(f"Invalid hex color format: '{hex_str}' (expected 6 hex digits)")
    try:
        r = int(cleaned[0:2], 16)
        g = int(cleaned[2:4], 16)
        b = int(cleaned[4:6], 16)
    except ValueError:
        raise ValueError(f"Invalid hex color characters in: '{hex_str}'")
    return (r, g, b)


def validate_file_exists(path: str, label: str) -> str:
    """Validate that a file exists and return its absolute path."""
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"{label} not found: {path}")
    return abs_path


def resolve_absolute_path(path: str, base_dir: str) -> str:
    """Resolve a path to absolute, joining with base_dir if relative."""
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(os.path.join(base_dir, path))


def ensure_directory(path: str) -> str:
    """Create a directory and all parents if they do not exist."""
    os.makedirs(path, exist_ok=True)
    return path


def setup_asset_directories(working_dir: str) -> dict[str, str]:
    """Create docsgen-assets/ with logos/ and source/ subdirectories under working_dir."""
    assets = os.path.abspath(os.path.join(working_dir, "docsgen-assets"))
    logos = os.path.join(assets, "logos")
    source = os.path.join(assets, "source")
    os.makedirs(logos, exist_ok=True)
    os.makedirs(source, exist_ok=True)
    return {"assets": assets, "logos": logos, "source": source}


def load_json_config(config_path: str) -> dict:
    """Read and validate a JSON config file, checking all required keys exist."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    required_keys = [
        "client_name",
        "client_logo",
        "company_logo",
        "primary_color",
        "accent_color",
        "language",
        "audience",
        "report_name",
        "version",
        "source_files",
        "output_dir",
    ]
    missing = [k for k in required_keys if k not in config]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")

    return config
