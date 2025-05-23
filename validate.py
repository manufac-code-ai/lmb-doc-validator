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
    
    args = parser.parse_args()
    
    # Run the validation with the parsed arguments
    run_validation(args)

if __name__ == "__main__":
    main()
