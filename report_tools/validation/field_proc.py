# report_tools/validation/field_processor.py
"""
Principled field identification and correction using format rules.
"""
import re
import logging
from rapidfuzz import fuzz
from report_tools.config_loader import get_field_definitions, load_correction_rules

class FieldProcessor:
    def __init__(self):
        self.field_definitions = get_field_definitions()
        self.correction_rules = load_correction_rules()
        self.field_format = self.correction_rules.get('field_format', {})
    
    def parse_field_components(self, text):
        """Extract field components using the principled pattern"""
        pattern = self.field_format.get('field_pattern', '')
        match = re.match(pattern, text)
        if not match:
            return None
            
        return {
            'original': text,
            'full_match': match.group(1),
            'field_name': match.group(2),
            'delimiter': match.group(3) or ':',
            'has_bold': '**' in text,
            'is_valid_structure': bool(match)
        }
    
    def identify_field_semantic(self, field_name):
        """Identify which canonical field this represents"""
        field_name_clean = field_name.lower().strip()
        
        # Direct semantic matching
        for field_id, field_def in self.field_definitions.items():
            canonical_clean = field_def['canonical'].replace('**', '').replace(':', '').replace('?', '').lower().strip()
            
            if field_name_clean == canonical_clean:
                return field_id, field_def['canonical']
            
            # Check semantic alternatives
            if 'semantic_alternatives' in field_def:
                for alt in field_def['semantic_alternatives']:
                    if field_name_clean == alt.lower().strip():
                        return field_id, field_def['canonical']
        
        # Fuzzy matching as fallback
        threshold = self.field_format.get('fuzzy_threshold', 90)
        best_score = 0
        best_field = None
        
        for field_id, field_def in self.field_definitions.items():
            canonical_clean = field_def['canonical'].replace('**', '').replace(':', '').replace('?', '').lower().strip()
            score = fuzz.ratio(field_name_clean, canonical_clean)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_field = (field_id, field_def['canonical'])
        
        return best_field if best_field else (None, None)
    
    def apply_format_rules(self, field_name, delimiter=':', field_id=None):
        """Apply formatting rules to create properly formatted field"""
        rules = self.field_format.get('rules', {})
        
        # Get the canonical field name if we identified the field
        if field_id and field_id in self.field_definitions:
            canonical = self.field_definitions[field_id]['canonical']
            # Extract delimiter from canonical form
            if '?' in canonical:
                delimiter = '?'
            else:
                delimiter = ':'
            # Extract clean field name from canonical
            field_name = canonical.replace('**', '').replace(':', '').replace('?', '').strip()
        
        # Apply formatting rules
        if rules.get('trim_whitespace', True):
            field_name = field_name.strip()
        
        if rules.get('bold_required', True) and rules.get('delimiter_inside_bold', True):
            return f"**{field_name}{delimiter}**"
        elif rules.get('bold_required', True):
            return f"**{field_name}**{delimiter}"
        else:
            return f"{field_name}{delimiter}"
    
    def process_field(self, text):
        """Complete field processing: identify, correct, and standardize"""
        # Parse the field structure
        components = self.parse_field_components(text)
        if not components:
            return None, None, False  # Not a field
        
        # Identify which field this is semantically
        field_id, canonical = self.identify_field_semantic(components['field_name'])
        if not field_id:
            return None, None, False  # Unrecognized field
        
        # Apply formatting rules to create corrected version
        corrected = self.apply_format_rules(
            components['field_name'], 
            components['delimiter'], 
            field_id
        )
        
        # Check if correction was needed
        needs_correction = text.strip() != corrected.strip()
        
        return field_id, corrected, needs_correction