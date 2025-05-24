"""
Configuration settings for validation of markdown documents.
This module centralizes all configurable parameters for document validation.

To use custom local paths, create config/config_loc.py with:
    SOURCE_DIR = "/your/path/to/markdown/files"  
    OUTPUT_DIR = "/your/custom/output/path"  # Optional - defaults to "_out"
"""
from pathlib import Path

# Try to import local configuration (not tracked in git)
try:
    from config.config_loc import *
except ImportError:
    # Default fallback if no local config exists
    SOURCE_DIR = "_in"
    # Other defaults will be defined below

# If OUTPUT_DIR wasn't defined in local config, use default
if 'OUTPUT_DIR' not in locals():
    OUTPUT_DIR = "_out"       # Base output directory

# Source directory configuration
RECURSIVE_SEARCH = True   # Whether to traverse subdirectories

# Output configuration
VALIDATED_DIR = "validated"  # Subdirectory for validation results

# Validation processing options
AUTO_CORRECTION_ENABLED = True  # Enable automatic formatting corrections
ANALYZE_ONLY = False   # Only analyze, don't move/copy files
MOVE_FILES = False     # When file operations occur, copy files (don't move them)
STRICT_VALIDATION = False    # Default to normalized validation
SHOW_VALID_REPORTS = False   # Whether to show valid reports in console output

# Directories to exclude from validation (customize for your use case)
VALIDATION_IGNORED_DIRECTORIES = [
    '_PM Reports',
    '_Diagnostic and Assist'
]

# File exclusion settings
IGNORE_FILE = "config/val_dir_ignore.txt"  # File containing list of directories to skip

# Log and analysis output configuration
LOG_DIR = "_logs"  # Directory for log files
LOG_FILE = f"{LOG_DIR}/val.log"  # Main validation log
SUMMARY_LOG = f"{LOG_DIR}/val_summary.txt"  # Validation report summary
ERROR_SUMMARY = f"{LOG_DIR}/val_errors.csv"  # CSV of error frequencies
RARE_ERRORS = f"{LOG_DIR}/val_rare.txt"      # List of rare errors
WORD_COUNT_CSV = f"{LOG_DIR}/val_words.csv"  # Word count analysis