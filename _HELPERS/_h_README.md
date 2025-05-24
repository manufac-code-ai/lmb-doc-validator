# Document Processing Helper Scripts

This directory contains utility scripts for the LMbridge document validator. While designed as a generic document processing tool, this implementation has been customized for working with AV integration service reports due to specific project requirements.

## Directory Structure

```
_HELPERS/
├── _h_INPUT/          # Place files to be processed here
├── _h_LOGS/           # Generated reports and logs appear here
├── _h_OUTPUT/         # Processed files appear here
├── doc_compare.py     # File matching utility
├── word2md.py         # Word document to Markdown converter
├── move_date2front.py # Date format standardization
├── doc_compare_skip.txt # Skip list for file matching
└── _h_README.md       # This file
```

## Available Scripts

### `doc_compare.py` - File Matching Utility

Compares files between directories to identify potential matches based on text similarity and naming patterns. Currently optimized for AV service report naming conventions.

**Usage:**

```bash
python doc_compare.py
```

**Current Features:**

- Text similarity matching with configurable thresholds
- Date format detection and comparison
- Skip list support for tracking user decisions
- Report generation with confidence scoring

### `word2md.py` - Document Converter

Converts Word documents (.docx) to Markdown (.md) files using pypandoc with line spacing cleanup.

**Usage:**

1. Place .docx files in `_h_INPUT/`
2. Run: `python word2md.py`
3. Converted files appear in `_h_OUTPUT/`

### `move_date2front.py` - Date Format Standardization

Moves trailing 6-digit dates to the beginning of filenames for consistent organization.

**Usage:**

1. Place files in `_h_INPUT/`
2. Run: `python move_date2front.py`
3. Renamed files appear in `_h_OUTPUT/`

**Example:** `Report Name 230426.md` → `230426 Report Name.md`

### `doc_compare_skip.txt` - Match Skip List

Tracks previously reviewed file matches to avoid re-processing.

**Format:**

```
newer_filename|legacy_filename|MATCH_or_NO_MATCH
```

## Workflow

1. Convert legacy documents with `word2md.py`
2. Standardize date formats with `move_date2front.py`
3. Compare file collections with `doc_compare.py`
4. Track decisions in `doc_compare_skip.txt`

## Requirements

- Python 3.7+
- pypandoc (for document conversion)
- Standard library modules: pathlib, re, datetime

## Notes

These scripts are part of the LMbridge utility suite. The current implementation includes optimizations for AV service report processing patterns, though the underlying framework remains generic. Scripts have been organized in the `_HELPERS` directory with standardized input/output/logs subdirectories for consistent workflow management.
