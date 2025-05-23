"""Core validation functions for individual reports."""

import os
import re
import logging
from report_tools.validation_fields import REQUIRED_FIELDS, FIELD_ALTERNATIVES
from report_tools.validation.auto_correction import auto_correct_document  # New import
from report_tools.config_loader import get_field_definitions  # New import

def normalize_markdown_content(content):
    """Normalize markdown content for consistent validation."""
    # Replace non-breaking spaces with regular spaces
    content = content.replace('\xa0', ' ')
    
    # Normalize line endings
    content = content.replace('\r\n', '\n')
    
    # Remove multiple blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

def validate_report(file_path, strict=False, auto_correct=False):
    """
    Validate a single report for required structure.
    
    Args:
        file_path: Path to the markdown file
        strict: Whether to use strict field matching
        auto_correct: Whether to apply auto-correction
        
    Returns:
        tuple: (is_valid, list_of_error_codes, corrected_content)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, [f"FILE_ERROR:{str(e)}"], None
    
    # Normalize content for consistent validation
    content = normalize_markdown_content(content)
    
    # Apply auto-correction if enabled
    corrected_content = None
    if auto_correct:
        corrected_content, correction_count = auto_correct_document(content)
        if correction_count > 0:
            logging.info(f"Made {correction_count} auto-corrections to {file_path.name}")
            # Use corrected content for validation
            content = corrected_content
    
    # Check for general structure issues
    if "**" not in content:
        return False, ["UNSTRUCTURED_DOCUMENT"], corrected_content
    
    errors = []
    content_lower = content.lower()  # Convert content to lowercase for case-insensitive comparison
    
    # Check for required fields
    for field in REQUIRED_FIELDS:
        field_lower = field.lower()  # Convert field to lowercase
        
        # Strict mode only accepts the exact field name with bold formatting
        if strict:
            if field in content:  # Keep strict mode exact for now
                found = True
            else:
                errors.append(f"MISSING_FIELD:{field}")
                continue
        
        # Default mode accepts alternative formattings from the alternatives dictionary (case-insensitive)
        else:
            found = False
            
            # First check if the exact field is present (case-insensitive)
            if field_lower in content_lower:
                found = True
            else:
                # Check alternatives if defined for this field (case-insensitive)
                alternatives = FIELD_ALTERNATIVES.get(field, [])
                for alt in alternatives:
                    if alt.lower() in content_lower:
                        found = True
                        break
            
            # Handle unbolded fields as a separate error type
            if not found:
                # Remove bold markers and check if plain text version exists (case insensitive)
                plain_field = field.replace('**', '').lower()
                if plain_field in content_lower:
                    errors.append(f"UNBOLDED_FIELD:{field.replace('**', '')}")
                else:
                    errors.append(f"MISSING_FIELD:{field}")
    
    return len(errors) == 0, errors, corrected_content