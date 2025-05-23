"""Core validation functions for individual reports."""

import os
import re
import logging
from report_tools.validation.field_proc import FieldProcessor
from report_tools.config_loader import get_field_definitions, get_document_types
from report_tools.validation.auto_correction import auto_correct_document  # New import

def normalize_markdown_content(content):
    """Normalize markdown content for consistent validation."""
    # Replace non-breaking spaces with regular spaces
    content = content.replace('\xa0', ' ')
    
    # Normalize line endings
    content = content.replace('\r\n', '\n')
    
    # Remove multiple blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

def detect_document_type(content, file_path=None):
    """Detect if document is PM report or service report - primarily filename-based"""
    
    # Debug logging
    logging.debug(f"Detecting document type for: {file_path.name if file_path else 'unknown'}")
    
    if file_path:
        import re
        # Check for PM followed by: space, end of filename, numeral, or +
        pm_pattern = r'\sPM(?:[\s.]|[1-9]|\+)'
        
        if re.search(pm_pattern, file_path.name):
            logging.debug(f"Classified as pm_report: filename contains PM pattern")
            return "pm_report"
    
    # Fallback: Only use explicit maintenance field indicators
    if "**maintenance performed?**" in content.lower():
        logging.debug(f"Classified as pm_report: maintenance field detected")
        return "pm_report"
    
    logging.debug(f"Classified as service_report: default")
    return "service_report"

def validate_report(file_path, strict=False, auto_correct=False):
    """
    Validate a single report for required structure.
    
    Args:
        file_path: Path to the markdown file
        strict: Whether to use strict field matching
        auto_correct: Whether to apply auto-correction
        
    Returns:
        tuple: (is_valid, list_of_error_codes, corrected_content, doc_type)
    """
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Normalize content
    content = normalize_markdown_content(content)
    
    # Apply auto-correction if enabled
    corrected_content = content
    correction_count = 0
    if auto_correct:
        corrected_content, correction_count = auto_correct_document(content)
    
    # DETECT DOCUMENT TYPE
    doc_type = detect_document_type(corrected_content, file_path)
    
    # Get required fields from detected document type
    doc_types = get_document_types()
    document_config = doc_types.get(doc_type, {})
    required_field_ids = document_config.get('required_fields', [])
    
    # Get field definitions
    field_definitions = get_field_definitions()
    
    # Convert field IDs to canonical names for validation
    required_fields = []
    for field_id in required_field_ids:
        if field_id in field_definitions:
            required_fields.append(field_definitions[field_id]['canonical'])
    
    # Initialize field processor
    processor = FieldProcessor()
    
    # Find fields in the document
    lines = corrected_content.split('\n')
    found_fields = set()
    error_codes = []
    
    # Process each line to identify fields
    for line in lines:
        if line.strip():
            field_id, corrected, needs_correction = processor.process_field(line)
            if field_id:
                # Convert field_id back to canonical name for comparison
                if field_id in field_definitions:
                    canonical = field_definitions[field_id]['canonical']
                    found_fields.add(canonical)
    
    # Check for missing required fields
    missing_fields = []
    for required_field in required_fields:
        if required_field not in found_fields:
            missing_fields.append(required_field)
            error_codes.append(f"MISSING_FIELD:{required_field}")
    
    # Check if document has any structure
    if not found_fields and required_fields:
        error_codes.append("UNSTRUCTURED_DOCUMENT")
    
    is_valid = len(missing_fields) == 0
    
    return is_valid, error_codes, corrected_content, doc_type  # Added doc_type