"""Batch processing of multiple report files."""

import os
import shutil
import logging
from pathlib import Path
from collections import Counter
import config.config as config
from report_tools import reporting
from report_tools.file_utils import find_markdown_files, get_ignored_reports
from report_tools.validation.core import validate_report

def process_folder(input_folder, output_base=config.OUTPUT_DIR, move_files=False, 
                  analyze_only=config.ANALYZE_ONLY, strict=config.STRICT_VALIDATION,
                  show_valid=config.SHOW_VALID_REPORTS, auto_correct=False):
    """
    Process markdown files and sort them into categories.
    
    Args:
        input_folder: Path to folder containing markdown files
        output_base: Base folder name for output
        move_files: Whether to move files (True) or copy them (False)
        analyze_only: If True, don't move/copy files, just analyze
        strict: Use strict validation
        show_valid: Show valid reports in console output
        auto_correct: Whether to apply auto-correction
        
    Returns:
        tuple: Stats for the processing run including corrections made
    """
    # Find all markdown files, potentially in subdirectories
    markdown_files = find_markdown_files(input_folder)
    
    if not markdown_files:
        print(f"No markdown files found in {input_folder}{' or its subdirectories' if config.RECURSIVE_SEARCH else ''}")
        return 0, 0, 0, {}, {}, 0
    
    # Create output directories with validated subdirectory
    validated_dir = Path(output_base) / config.VALIDATED_DIR
    valid_dir = validated_dir / "valid"
    invalid_dir = validated_dir / "invalid"
    
    valid_dir.mkdir(exist_ok=True, parents=True)
    invalid_dir.mkdir(exist_ok=True, parents=True)
    
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(config.SUMMARY_LOG), exist_ok=True)
    
    total_files = 0
    valid_files = 0
    invalid_files = 0
    ignored_files = 0
    error_counter = Counter()
    file_errors = {}
    
    # Get list of reports to ignore
    ignored_reports = get_ignored_reports()
    
    # Structures for tracking word counts
    word_counts = {
        "valid": [],
        "invalid": []
    }
    file_word_counts = {}
    
    # Counter for auto-corrections
    total_corrections = 0
    
    with open(config.SUMMARY_LOG, 'w', encoding='utf-8') as log:
        log.write("Report Validation Summary\n")
        log.write("=======================\n\n")
        
        for file_path in markdown_files:
            total_files += 1
            
            # Check if this file should be ignored
            if file_path.name in ignored_reports:
                log.write(f"⚠️ IGNORED: {file_path.name} (explicitly excluded from validation)\n")
                logging.info(f"Skipping validation for ignored report: {file_path.name}")
                ignored_files += 1
                continue
            
            # Count words in the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                word_count = len(content.split())
                file_word_counts[file_path.name] = word_count
            
            # Validate the report
            is_valid, error_codes, corrected_content, doc_type = validate_report(file_path, strict=strict, auto_correct=auto_correct)
            
            # Store the file's error codes for summary
            file_errors[file_path.name] = error_codes
            
            # Update error counter for CSV summary
            for error in error_codes:
                error_counter[error] += 1
            
            if is_valid:
                valid_files += 1
                word_counts["valid"].append(word_count)
                
                # Determine output directory based on document type
                if doc_type == "pm_report":
                    output_dir = os.path.join(output_base, config.VALIDATED_DIR, "valid PM")
                else:
                    output_dir = os.path.join(output_base, config.VALIDATED_DIR, "valid")
                
                # Create the output directory
                os.makedirs(output_dir, exist_ok=True)
                
                log.write(f"✅ VALID: {file_path.name} ({word_count} words)\n")
                if show_valid:
                    logging.info(f"Valid report: {file_path.name}")
                    
            else:
                invalid_files += 1
                word_counts["invalid"].append(word_count)
                
                output_dir = os.path.join(output_base, config.VALIDATED_DIR, "invalid")
                
                # Create the output directory
                os.makedirs(output_dir, exist_ok=True)
                
                log.write(f"❌ INVALID: {file_path.name} ({word_count} words)\n")
                log.write(f"  Errors: {', '.join(error_codes)}\n")
                logging.debug(f"INVALID: {file_path.name} - Errors: {error_codes}")
            
            # Handle file copying/moving and auto-correction
            if not analyze_only:
                destination = Path(output_dir) / file_path.name
                
                # Check if we need to write corrected content
                if auto_correct and corrected_content and corrected_content != content:
                    total_corrections += 1
                    # Write corrected content directly
                    with open(destination, 'w', encoding='utf-8') as f:
                        f.write(corrected_content)
                else:
                    # Normal copy/move operation
                    if move_files:
                        shutil.move(str(file_path), str(destination))
                    else:
                        shutil.copy2(str(file_path), str(destination))
            else:
                # In analyze-only mode, just count corrections
                if auto_correct and corrected_content and corrected_content != content:
                    total_corrections += 1
                    logging.info(f"Corrections available for {file_path.name}")
    
    # Calculate word count statistics
    word_stats = reporting.calculate_word_statistics(word_counts)
    
    # Generate reporting files
    reporting.write_summary_files(file_errors, file_word_counts, word_stats, error_counter)
    
    return valid_files, invalid_files, ignored_files, error_counter, word_stats, total_corrections