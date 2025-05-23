#!/usr/bin/env python3
"""Validate markdown service reports for proper structure."""

import argparse
import config.config as config
from report_tools.validation import run_validation

def main():
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(description='Validate markdown service reports structure.')
    parser.add_argument('--input', default=config.SOURCE_DIR, 
                        help=f'Input folder containing markdown reports')
    parser.add_argument('--output', default=config.OUTPUT_DIR, 
                        help=f'Base output folder')
    parser.add_argument('--move', action='store_true', default=False,
                        help='Move files instead of copying them')
    parser.add_argument('--analyze-only', action='store_true', default=config.ANALYZE_ONLY,
                        help='Analyze only, do not move/copy files')
    parser.add_argument('--strict', action='store_true', default=config.STRICT_VALIDATION,
                        help='Use strict validation')
    parser.add_argument('--show-valid', action='store_true', default=config.SHOW_VALID_REPORTS,
                        help='Show valid reports in output')
    
    args = parser.parse_args()
    
    # Run the validation with the parsed arguments
    run_validation(args)

if __name__ == "__main__":
    main()
