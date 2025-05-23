"""
Field matching implementation using tiered approach:
1. Direct matching
2. Pattern matching 
3. Fuzzy matching (as fallback)
"""
import re
import logging
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
        
        # Check patterns (for backward compatibility)
        if 'patterns' in field_def:
            for pattern in field_def['patterns']:
                if field_text == pattern:
                    return field_id, field_def['canonical']
        
        # Generate explicit matches from semantic alternatives
        if 'semantic_alternatives' in field_def:
            # Generate variations from each semantic alternative
            for alt in field_def['semantic_alternatives']:
                # Both bold forms
                bold_inside = f"**{alt}:**"
                bold_outside = f"**{alt}**:"
                
                # Question mark variations if specified
                if field_def.get('question_mark', False):
                    bold_inside_q = f"**{alt}?**"
                    bold_outside_q = f"**{alt}**?"
                    if field_text in [bold_inside_q, bold_outside_q]:
                        return field_id, field_def['canonical']
                
                # Direct match against generated patterns
                if field_text in [bold_inside, bold_outside]:
                    return field_id, field_def['canonical']
    
    return None, None


def generate_variations(base_text, field_def):
    """
    Generate all possible variations of a field based on flags
    
    Args:
        base_text: Base text to generate variations from
        field_def: Field definition with flags
        
    Returns:
        list: All possible variations
    """
    variations = [base_text]
    
    # Handle plurals if allowed
    if field_def.get('allow_plural', False):
        if base_text.endswith('y'):
            # Handle y -> ies pluralization
            variations.append(base_text[:-1] + 'ies')
        else:
            # Simple pluralization
            variations.append(base_text + 's')
    
    # Handle capitalization variations if allowed
    if field_def.get('allow_capital', False):
        # Add capitalized versions
        for var in list(variations):  # Use list() to avoid modifying during iteration
            variations.append(var.capitalize())
    
    return variations


def pattern_match(field_text, field_definitions=None):
    """
    Use pattern matching for field identification with semantic alternatives
    
    Args:
        field_text: The field text to match
        field_definitions: Optional field definitions (loaded if not provided)
        
    Returns:
        tuple: (field_id, canonical_form) or (None, None) if no match
    """
    if field_definitions is None:
        field_definitions = get_field_definitions()
    
    # Strip formatting for content comparison
    clean_text = re.sub(r'\*\*', '', field_text).strip()
    clean_text = re.sub(r'[\:\?]', '', clean_text).strip()
    
    for field_id, field_def in field_definitions.items():
        # First check canonical form
        canonical = field_def['canonical']
        clean_canonical = re.sub(r'\*\*', '', canonical).strip()
        clean_canonical = re.sub(r'[\:\?]', '', clean_canonical).strip()
        
        # Build variations based on field properties
        variations = [clean_canonical.lower()]
        
        # Add variations from semantic alternatives
        if 'semantic_alternatives' in field_def:
            for alt in field_def['semantic_alternatives']:
                # Generate all variations based on flags
                alt_variations = generate_variations(alt.lower(), field_def)
                variations.extend(alt_variations)
        
        # Legacy support for patterns
        if 'patterns' in field_def:
            for pattern in field_def['patterns']:
                pattern_clean = re.sub(r'\*\*', '', pattern).strip()
                pattern_clean = re.sub(r'[\:\?]', '', pattern_clean).strip()
                variations.append(pattern_clean.lower())
        
        # Check against all variations
        if clean_text.lower() in variations:
            return field_id, field_def['canonical']
        
        # Additional regex matching for special cases
        for var in variations:
            if re.match(f'^{re.escape(var)}s?$', clean_text.lower()):
                return field_id, field_def['canonical']
    
    return None, None


def fuzzy_match(field_text, field_definitions=None, threshold=90):
    """
    Use fuzzy matching for field identification with smart preprocessing
    
    Args:
        field_text: The field text to match
        field_definitions: Optional field definitions (loaded if not provided)
        threshold: Similarity threshold (0-100)
        
    Returns:
        tuple: (field_id, canonical_form) or (None, None) if no match
    """
    if field_definitions is None:
        field_definitions = get_field_definitions()
    
    best_match = None
    best_field_id = None
    best_score = 0
    
    # IMPROVED: Preserve formatting signals instead of stripping them
    # This helps recognize proper field formatting in the matching
    clean_field_text = field_text
    # Normalize whitespace
    clean_field_text = re.sub(r'\s+', ' ', clean_field_text).strip()
    # Mark bold tags with special tokens to preserve in matching
    has_bold_start = '**' in clean_field_text
    clean_field_text = re.sub(r'\*\*', 'BOLD', clean_field_text)
    
    # Check for the presence of colons or question marks (formatting signals)
    has_delimiter = ':' in clean_field_text or '?' in clean_field_text
    
    logging.debug(f"Fuzzy matching: '{field_text}' → '{clean_field_text}'")
    
    # Check each field definition
    for field_id, field_def in field_definitions.items():
        canonical = field_def['canonical']
        
        # Process canonical form with the same transformations
        clean_canonical = canonical
        clean_canonical = re.sub(r'\s+', ' ', clean_canonical).strip()
        canonical_has_bold = '**' in clean_canonical
        clean_canonical = re.sub(r'\*\*', 'BOLD', clean_canonical)
        
        # Basic content similarity
        base_score = fuzz.ratio(clean_field_text.lower(), clean_canonical.lower())
        
        # IMPROVED: Apply formatting bonus when formatting signals match
        format_bonus = 0
        if has_bold_start == canonical_has_bold:
            format_bonus += 5  # Bonus for matching bold formatting
        if has_delimiter:
            format_bonus += 5  # Bonus for having a delimiter

        # Calculate adjusted score
        adjusted_score = min(base_score + format_bonus, 100)
        
        if adjusted_score > best_score:
            best_score = adjusted_score
            best_field_id = field_id
            best_match = canonical
            logging.debug(f"New best match: '{canonical}' (score: {base_score} + {format_bonus} = {adjusted_score})")
    
    # Only return if score is above threshold
    if best_score >= threshold:
        return best_field_id, best_match
    
    return None, None


def identify_field(field_text):
    """
    Identify field using tiered matching approach
    
    Args:
        field_text: The field text to identify
        
    Returns:
        tuple: (field_id, canonical_form) or (None, None) if not identified
    """
    # Load field definitions once
    field_definitions = get_field_definitions()
    
    # Try direct match first (fastest)
    field_id, canonical = direct_match(field_text, field_definitions)
    if field_id:
        return field_id, canonical
    
    # Try pattern match next
    field_id, canonical = pattern_match(field_text, field_definitions)
    if field_id:
        return field_id, canonical
    
    # Finally try fuzzy match (most flexible)
    field_id, canonical = fuzzy_match(field_text, field_definitions)
    return field_id, canonical