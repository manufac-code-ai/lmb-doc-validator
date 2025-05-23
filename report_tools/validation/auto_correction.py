"""
Auto-correction functionality using a principled approach to field formatting.
Applies a standard field format rather than specific error-focused rules.
"""
import re
import logging
from report_tools.config_loader import load_correction_rules, get_field_definitions
from report_tools.validation.field_matcher import identify_field


def extract_field_name(text):
    """Extract field name from text with various formatting."""
    return re.sub(r'[\*\:\?]', '', text).strip()


def extract_delimiter(text):
    """Extract delimiter (: or ?) from field text."""
    if '?' in text:
        return '?'
    return ':'


def get_standard_format():
    """Get the standard field format from configuration."""
    rules = load_correction_rules()
    return rules.get('field_format', {}).get('standard_format', "**{field_name}{delimiter}**")


def standardize_field(field_text, field_id=None, canonical=None):
    """
    Apply standard format to field based on fundamental rules.
    
    Args:
        field_text: The field text to correct
        field_id: Optional field ID if already identified
        canonical: Optional canonical form
        
    Returns:
        str: Corrected field text using standard format
    """
    # Identify the field if not provided
    if not field_id or not canonical:
        field_id, canonical = identify_field(field_text)
        
    if not field_id:
        return field_text  # Can't correct if we don't know what field it is
    
    # Extract the field name from the canonical form
    field_name = extract_field_name(canonical)
    
    # Determine the correct delimiter (: or ?)
    delimiter = extract_delimiter(canonical)
    
    # Get the standard format and apply it
    standard_format = get_standard_format()
    corrected_field = standard_format.format(field_name=field_name, delimiter=delimiter)
    
    if corrected_field != field_text:
        logging.debug(f"Standardized field format: '{field_text}' -> '{corrected_field}'")
    
    return corrected_field


def auto_correct_document(content):
    """
    Auto-correct document fields using the principled approach.
    
    Args:
        content: Document content
        
    Returns:
        tuple: (corrected_content, correction_count)
    """
    lines = content.split('\n')
    corrected_lines = []
    correction_count = 0
    
    # Get field pattern from configuration
    rules = load_correction_rules()
    field_pattern = rules.get('field_format', {}).get('field_pattern', 
                                              r'^(?:\s*)((?:\*\*)?[A-Za-z\s]+(?:\*\*)?[:\?]?)')
    
    for line in lines:
        match = re.match(field_pattern, line)
        if match:
            # Potential field found - the whole match is group 1
            field_text = match.group(1)
            field_id, canonical = identify_field(field_text)
            
            if field_id:
                # Field identified, standardize its format
                corrected_field = standardize_field(field_text, field_id, canonical)
                
                if corrected_field != field_text:
                    # Field was corrected
                    correction_count += 1
                    line = line.replace(field_text, corrected_field)
        
        corrected_lines.append(line)
    
    return '\n'.join(corrected_lines), correction_count