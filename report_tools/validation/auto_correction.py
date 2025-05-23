"""
Document auto-correction using principled field processing.
"""
import re
import logging
from .field_proc import FieldProcessor


def auto_correct_document(content):
    """Apply auto-corrections to document content while preserving field values"""
    processor = FieldProcessor()
    lines = content.split('\n')
    corrected_lines = []
    correction_count = 0

    for line in lines:
        # Check if line might be a field header with content
        field_match = re.match(r'^\s*((?:\*\*)?[A-Za-z\s]+(?:\*\*)?[:\?]?)\s*(.*)', line)
        
        if field_match:
            potential_header = field_match.group(1)
            field_content = field_match.group(2)  # Everything after the header
            
            # Try to process just the header part
            field_id, corrected_header, needs_correction = processor.process_field(potential_header)
            
            if needs_correction and corrected_header:
                # Clean up any extra bold formatting from field_content
                clean_content = field_content.strip()
                # Remove leading bold asterisks if they exist
                clean_content = re.sub(r'^\*\*\s*', '', clean_content)
                
                # Combine corrected header with cleaned content
                corrected_line = corrected_header
                if clean_content:
                    corrected_line += " " + clean_content
                
                logging.debug(f"Corrected field: '{line.strip()}' → '{corrected_line}'")
                corrected_lines.append(corrected_line)
                correction_count += 1
            else:
                # No correction needed, keep original line
                corrected_lines.append(line)
        else:
            # Not a field header, keep as-is
            corrected_lines.append(line)

    return '\n'.join(corrected_lines), correction_count