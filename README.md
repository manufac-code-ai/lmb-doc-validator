# LMbridge Document Validator

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A configurable document validation and preprocessing tool for standardizing technical reports before LLM processing. Part of the LMbridge suite for bridging local documents to Large Language Model systems.

## Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Features](#features)
- [Usage](#usage)
- [Configuration](#configuration)
- [Output Structure](#output-structure)
- [Customization](#customization)
- [Helper Scripts](#helper-scripts)

## Overview

The Document Validator cleans and standardizes technical reports to ensure consistent structure before feeding them into downstream processing tools like `lmb-doc-stacker`. While designed as a generic validation framework, this implementation is currently configured for technical report formats with structured field requirements.

**Typical Workflow:**

1. **Raw Technical Reports** → LMbridge Doc Validator → **Standardized Reports**
2. **Standardized Reports** → LMbridge Doc Stacker → **LLM-Ready Stacks**
3. **LLM-Ready Stacks** → NotebookLM/Claude/ChatGPT → **Queryable Knowledge Base**

## Quick Start

```bash
# Validate documents (analyze-only mode)
python validate.py --input /path/to/reports --analyze-only

# Clean and organize documents
python validate.py --input /path/to/reports --output /path/to/clean

# Move files instead of copying
python validate.py --input /path/to/reports --move
```

## Features

### Document Processing

- **Multi-format Support**: Processes markdown (.md) files with configurable extensions
- **Auto-categorization**: Sorts documents by type (currently: Service Reports, PM Reports)
- **Field Validation**: Ensures required fields are present and properly formatted
- **Auto-correction**: Fixes common formatting issues (bold markers, delimiters, whitespace)
- **Flexible Matching**: Handles field name variations and alternative spellings

### Analysis & Reporting

- **Comprehensive Statistics**: Document counts, validation rates, error frequency
- **Multiple Output Formats**: Console summaries, CSV exports, detailed logs
- **Error Categorization**: Groups validation issues by type and frequency
- **Word Count Analysis**: Tracks document length statistics

### Processing Modes

- **Analyze-only**: Validation without file operations
- **Copy Mode**: Preserves original files (default)
- **Move Mode**: Relocates files during processing
- **Strict vs. Normalized**: Configurable validation approaches

## Usage

### Basic Commands

```bash
# Analyze documents without moving files
python validate.py --analyze-only

# Process with custom input/output paths
python validate.py --input /source/docs --output /clean/docs

# Move files instead of copying
python validate.py --move

# Show valid documents in output (normally hidden)
python validate.py --show-valid

# Use strict validation rules
python validate.py --strict
```

### Command Line Options

| Option           | Description                               | Default             |
| ---------------- | ----------------------------------------- | ------------------- |
| `--input`        | Source directory containing reports       | `config.SOURCE_DIR` |
| `--output`       | Destination directory for processed files | `config.OUTPUT_DIR` |
| `--move`         | Move files instead of copying             | False (copy)        |
| `--analyze-only` | Validate without file operations          | False               |
| `--strict`       | Use strict validation rules               | False               |
| `--show-valid`   | Include valid files in output             | False               |

## Configuration

### Local Paths (Optional)

To use custom source and output paths, create `config/config_loc.py`:

```python
# Local source directory
SOURCE_DIR = "/path/to/your/markdown/files"

# Optional: Custom output directory (defaults to "_out")
OUTPUT_DIR = "/path/to/your/output"
```

This file is automatically ignored by git to keep your local paths private.

### Document Structure Configuration

The validator uses YAML configuration files in `config/rules/` to define document structures:

### Document Types (`config/rules/doc_types.yaml`)

Defines the categories of documents and their expected field sets:

```yaml
document_types:
  technical_report:
    name: "Technical Report"
    description: "Standard technical work or project report"
    required_fields:
      - date_of_work
      - author_name
      - client_contact
      - issue_description
      - work_performed
      - status_resolved
      - next_steps
```

### Field Definitions (`config/rules/fields.yaml`)

Configures field names, aliases, and validation patterns:

```yaml
fields:
  date_of_work:
    display: "Date of work"
    canonical: "**Date of work:**"
    semantic_alternatives:
      - "Work date"
      - "Date"
      - "Date performed"

  author_name:
    display: "Author name"
    canonical: "**Author name:**"
    semantic_alternatives:
      - "Author"
      - "Performed by"
      - "Staff member"
```

### Correction Rules (`config/rules/correction_rules.yaml`)

Defines automatic formatting corrections:

```yaml
field_format:
  standard_format: "**{field_name}{delimiter}**"
  rules:
    bold_required: true
    delimiter_inside_bold: true
    trim_whitespace: true
```

### Directory Exclusions (`config/val_dir_ignore.txt`)

Lists directories to skip during processing:

```
_PM Reports
_Diagnostic and Assist
```

## Output Structure

The validator organizes processed documents into logical categories:

```
output/
├── valid_service/          # Valid service reports
├── valid_pm/              # Valid PM reports
├── invalid/               # Documents requiring manual review
├── analysis/
│   ├── validation_summary.txt
│   ├── error_frequency.csv
│   ├── word_count_analysis.csv
│   └── rare_errors.csv
└── logs/
    └── validation.log
```

### Report Categories

- **Valid Service**: Documents matching service report structure
- **Valid PM**: Documents matching PM report structure
- **Invalid**: Documents with validation errors requiring review

## Customization

This validator is configured for a specific technical report format. To adapt it for your documents:

### 1. Define Your Document Types

Edit `config/doc_types.yaml` to match your document categories:

```yaml
document_types:
  incident_report:
    display_name: "Incident Report"
    required_fields:
      - incident_id
      - date_reported
      - severity
      - description
      - response_actions
```

### 2. Configure Field Definitions

Update `config/fields.yaml` with your field names and patterns:

```yaml
canonical_fields:
  incident_id:
    aliases: ["ticket_id", "case_number", "ref_number"]
    pattern: "**Incident ID:**"
```

### 3. Set Correction Rules

Adjust `config/correction_rules.yaml` for your formatting preferences:

```yaml
correction_rules:
  field_formatting:
    enabled: true
    require_bold_field_names: true
    standardize_delimiters: true
```

### 4. Update Processing Logic

Modify `report_tools/validation_fields.py` to handle your specific field validation requirements.

## Helper Scripts

The `_HELPERS/` directory contains utilities for document preprocessing:

- **`doc_compare.py`**: Match and compare document collections
- **`word2md.py`**: Convert Word documents to Markdown
- **`move_date2front.py`**: Standardize filename date formats

See `_HELPERS/_h_README.md` for detailed helper documentation.

## Requirements

- Python 3.7+
- PyYAML
- Standard library modules: pathlib, re, csv, logging

## Integration with LMbridge Suite

This validator works as part of the LMbridge document processing pipeline:

1. **LMbridge Doc Validator** (this tool) → Clean, standardized documents
2. **LMbridge Doc Stacker** → Consolidated files for LLM processing
3. **LLM Systems** → Queryable knowledge bases

The validator ensures clean input for better downstream processing and LLM understanding.

## Notes

While designed as a generic validation framework, this implementation includes specific configurations for technical report processing. The YAML-based configuration system allows adaptation to different document types and organizational requirements. Most users will need to customize the field definitions and document types to match their specific use cases.
