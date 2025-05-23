"""
Field matching implementation using tiered approach:
1. Direct matching
2. Pattern matching 
3. Fuzzy matching (as fallback)
"""
import re
from rapidfuzz import fuzz
from report_tools.config_loader import get_field_definitions


def get_canonical_fields():
    """Get list of canonical field names"""
    fields = get_field_definitions()
    return {field_id: data['canonical'] for field_id, data in fields.items()}


def direct_match(field_text, field_definitions=None):
    """
    Check if field exactly matches a canonical name or alternative
    
    Args:
        field_text: The field text to match
        field_definitions: Optional field definitions (loaded if not provided)
        
    Returns:
        tuple: (field_id, canonical_form) or (None, None) if no match
    """
    if field_definitions is None:
        field_definitions = get_field_definitions()
    
    # Check each field definition
    for field_id, field_def in field_definitions.items():
        # Check canonical form
        if field_text == field_def['canonical']:
            return field_id, field_def['canonical']
        
        # Check patterns
        if 'patterns' in field_def:
            for pattern in field_def['patterns']:
                if field_text == pattern:
                    return field_id, field_def['canonical']
    
    return None, None


def pattern_match(field_text, field_definitions=None):
    """
    Use regex patterns to match fields with predictable variations
    
    Args:
        field_text: The field text to match
        field_definitions: Optional field definitions (loaded if not provided)
        
    Returns:
        tuple: (field_id, canonical_form) or (None, None) if no match
    """
    if field_definitions is None:
        field_definitions = get_field_definitions()
    
    # Convert patterns to regex patterns
    for field_id, field_def in field_definitions.items():
        # Check patterns
        if 'patterns' in field_def:
            for pattern in field_def['patterns']:
                # Convert simple string patterns to regex
                # This handles * as literal asterisks in markdown
                pattern_regex = pattern.replace('*', '\\*').replace('?', '\\?')
                
                # For plurals like "problem(s)"
                pattern_regex = pattern_regex.replace('[[s]]', '(?:s)?')
                
                # Now it's a proper regex pattern
                if re.match(f"^{pattern_regex}$", field_text):
                    return field_id, field_def['canonical']
    
    return None, None


def fuzzy_match(field_text, threshold=90, field_definitions=None):
    """
    Fallback fuzzy matching for field names
    
    Args:
        field_text: The field text to match
        threshold: Minimum similarity score (0-100)
        field_definitions: Optional field definitions (loaded if not provided)
        
    Returns:
        tuple: (field_id, canonical_form) or (None, None) if no match
    """
    if field_definitions is None:
        field_definitions = get_field_definitions()
    
    best_match = None
    best_score = 0
    best_field_id = None
    
    # Strip formatting for better comparison
    clean_field_text = re.sub(r'[\*\:]', '', field_text).strip()
    
    for field_id, field_def in field_definitions.items():
        # Get clean canonical text
        canonical = field_def['canonical']
        clean_canonical = re.sub(r'[\*\:]', '', canonical).strip()
        
        # Calculate similarity
        score = fuzz.ratio(clean_field_text.lower(), clean_canonical.lower())
        
        if score > best_score:
            best_score = score
            best_match = canonical
            best_field_id = field_id
    
    # Only return if score is above threshold
    if best_score >= threshold:
        return best_field_id, best_match
    
    return None, None


def identify_field(field_text, fuzzy_threshold=90):
    """
    Identify a field using tiered matching approach
    
    Args:
        field_text: The field text to match
        fuzzy_threshold: Threshold for fuzzy matching
        
    Returns:
        tuple: (field_id, canonical_form) or (None, None) if no match
    """
    field_definitions = get_field_definitions()
    
    # Tier 1: Direct match
    field_id, canonical = direct_match(field_text, field_definitions)
    if field_id:
        return field_id, canonical
    
    # Tier 2: Pattern match
    field_id, canonical = pattern_match(field_text, field_definitions)
    if field_id:
        return field_id, canonical
    
    # Tier 3: Fuzzy match (fallback)
    field_id, canonical = fuzzy_match(field_text, fuzzy_threshold, field_definitions)
    if field_id:
        return field_id, canonical
    
    return None, None