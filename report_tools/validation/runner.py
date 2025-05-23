"""High-level validation runner handling CLI and orchestration."""

import os
import logging
import config.config as config
from report_tools.file_utils import setup_logger, find_markdown_files
from report_tools.validation.processor import process_folder
from pathlib import Path

def run_validation(args):
    """Run the validation process with the provided arguments."""
    # Print a blank line at the start for separation from command
    print("")
    
    # Setup logger
    setup_logger()
    
    # Get settings from config
    recursive = config.RECURSIVE_SEARCH
    show_valid = config.SHOW_VALID_REPORTS
    analyze_only = config.ANALYZE_ONLY
    strict = config.STRICT_VALIDATION
    auto_correct = config.AUTO_CORRECTION_ENABLED
    move_files = config.MOVE_FILES  # Use the dedicated setting
    
    # Make sure input folder exists
    if not os.path.exists(args.input):
        os.makedirs(args.input)
        print(f"Created input folder: {args.input}")
        print(f"Please place your markdown reports in this folder and run the script again.")
        return
    
    # Make sure output base folder exists
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Add blank line before starting message
    print("")
    print(f"Starting report validation from {args.input}" + 
          (" (including subdirectories)" if recursive else ""))
    
    # Add a blank line before configuration info
    print("")
    if strict:
        print("Using strict validation (no normalization)")
    else:
        print("Using normalized validation (accepting alternate field formats)")
    
    if auto_correct:
        print("Auto-correction is enabled for field formatting issues")
    
    # Add a blank line before processing mode
    print("")
    if analyze_only:
        print("Analyze-only mode: files will be analyzed but not moved/copied")
    else:
        if move_files:
            print("Processing mode: files will be moved to output folders")
        else:
            print("Processing mode: files will be copied to output folders")
    
    # Get total files including ignored directories
    ignored_count = 0
    if recursive:
        # This is already filtering ignored directories in find_markdown_files
        pass
        
    # Run the validation
    valid, invalid, ignored_files, error_counter, word_stats, corrections = process_folder(
        args.input,
        output_base=args.output,
        move_files=config.MOVE_FILES,           # Use config default
        analyze_only=config.ANALYZE_ONLY,       # Use config default  
        strict=config.STRICT_VALIDATION,        # Use config default
        show_valid=config.SHOW_VALID_REPORTS,   # Use config default
        auto_correct=auto_correct
    )
    
    # Count PM reports from the output directory
    valid_pm_dir = Path(args.output) / config.VALIDATED_DIR / "valid PM"
    valid_pm_count = 0
    if valid_pm_dir.exists():
        valid_pm_count = len(list(valid_pm_dir.glob('*.md')))
    
    valid_service_count = valid - valid_pm_count

    # Updated console output
    print(f"\nProcessing complete! Valid Service: {valid_service_count}, Valid PM: {valid_pm_count}, Invalid: {invalid}")

    # Fixed word stats output - use the correct structure
    if valid > 0:
        print(f"Valid reports average length: {word_stats['valid']['average']:.1f} words (range: {word_stats['valid']['min']} to {word_stats['valid']['max']} words)")

    if invalid > 0:
        print(f"Invalid reports average length: {word_stats['invalid']['average']:.1f} words (range: {word_stats['invalid']['min']} to {word_stats['invalid']['max']} words)")

    # Add a newline before file references
    print("")
    
    if valid + invalid > 0:
        print(f"See {config.SUMMARY_LOG} for details")
        print(f"Word count analysis in {config.WORD_COUNT_CSV}")
        print(f"Error frequency analysis in {config.ERROR_SUMMARY}")
        
        # Print rare errors reference with better spacing
        if error_counter:
            # Add double newline for visual separation
            print(f"\n\nSee {config.RARE_ERRORS} for complete details")
            
            # Print top 5 most common errors
            print("\nTop issues found:")
            for error, count in sorted(error_counter.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {error}: {count} occurrences")
    
    if corrections and corrections > 0:
        print(f"Auto-correction applied {corrections} formatting fixes")
    
    # Add final newline to separate from next terminal prompt
    print("")