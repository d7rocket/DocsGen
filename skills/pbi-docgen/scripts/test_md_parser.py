"""Tests for md_parser.py - Markdown section detection and extraction."""

import os
import tempfile
import unittest


class TestParseMarkdownSources(unittest.TestCase):
    """Tests for the parse_markdown_sources function."""

    def _write_temp_file(self, content: str) -> str:
        """Write content to a temporary file and return its path."""
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
        f.write(content)
        f.close()
        self._temp_files.append(f.name)
        return f.name

    def setUp(self):
        self._temp_files = []

    def tearDown(self):
        for path in self._temp_files:
            try:
                os.unlink(path)
            except OSError:
                pass

    def test_single_file_three_sections(self):
        """Test 1: Single file with 3 ## headings matching overview, mquery, datamodel returns dict with exactly those 3 keys."""
        from scripts.md_parser import parse_markdown_sources

        content = """# Title
## Project Overview
This is an overview of the project.

## M Query Logic
Here is the M query content.

## Data Model Details
The data model has these tables.
"""
        path = self._write_temp_file(content)
        result = parse_markdown_sources([path])
        self.assertEqual(set(result.keys()), {"overview", "mquery", "datamodel"})
        self.assertIn("overview of the project", result["overview"]["content"])
        self.assertIn("M query content", result["mquery"]["content"])
        self.assertIn("data model has these tables", result["datamodel"]["content"])

    def test_heading_inside_code_block_not_detected(self):
        """Test 2: Heading inside a fenced code block is NOT detected as a section."""
        from scripts.md_parser import parse_markdown_sources

        content = """## Project Overview
Real overview content here.

```
## Fake Heading Inside Code Block
This should not be detected.
```

## Data Model Info
Real data model content.
"""
        path = self._write_temp_file(content)
        result = parse_markdown_sources([path])
        self.assertIn("overview", result)
        self.assertIn("datamodel", result)
        # There should be no extra sections from the code block
        self.assertEqual(len(result), 2)

    def test_no_matching_headings_returns_empty(self):
        """Test 3: File with no matching headings returns empty dict."""
        from scripts.md_parser import parse_markdown_sources

        content = """# Top Level Only
Some body text here.

## Unrelated Random Heading
More text that does not match any known section keywords.
"""
        path = self._write_temp_file(content)
        result = parse_markdown_sources([path])
        self.assertEqual(result, {})

    def test_data_source_configuration_matches_sources(self):
        """Test 4: Heading 'Data Source Configuration' matches section ID 'sources'."""
        from scripts.md_parser import parse_markdown_sources

        content = """## Data Source Configuration
The data sources connect to SQL Server via gateway.
"""
        path = self._write_temp_file(content)
        result = parse_markdown_sources([path])
        self.assertIn("sources", result)
        self.assertEqual(result["sources"]["label"], "Source Systems & Architecture")

    def test_multiple_files_concatenated(self):
        """Test 5: Multiple files are concatenated - sections from both files appear in output."""
        from scripts.md_parser import parse_markdown_sources

        content1 = """## Project Overview
Overview from file one.
"""
        content2 = """## Data Model Summary
Data model from file two.
"""
        path1 = self._write_temp_file(content1)
        path2 = self._write_temp_file(content2)
        result = parse_markdown_sources([path1, path2])
        self.assertIn("overview", result)
        self.assertIn("datamodel", result)

    def test_empty_section_excluded(self):
        """Test 6: Section with heading but no body content is excluded."""
        from scripts.md_parser import parse_markdown_sources

        content = """## Project Overview

## Data Model Info
Actual content here.
"""
        path = self._write_temp_file(content)
        result = parse_markdown_sources([path])
        # Overview has no content below it (just blank line then next heading)
        self.assertNotIn("overview", result)
        self.assertIn("datamodel", result)

    def test_case_insensitive_keyword_matching(self):
        """Test 7: Keywords are matched case-insensitively."""
        from scripts.md_parser import parse_markdown_sources

        content = """## PROJECT OVERVIEW
All caps overview content here.
"""
        path = self._write_temp_file(content)
        result = parse_markdown_sources([path])
        self.assertIn("overview", result)
        self.assertIn("All caps overview content", result["overview"]["content"])


if __name__ == "__main__":
    unittest.main()
