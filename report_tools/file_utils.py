"""File utilities for finding and filtering markdown reports."""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import config.config as config

def setup_logger(log_file=config.LOG_FILE, console_level=logging.WARNING):
    """
    Set up logging to both console and file.
    
    Args:
        log_file: Path to log file
        console_level: Logging level for console output (default: WARNING)
    """
    # Create log directory if it doesn't exist
    log_dir = Path(log_file).parent
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
        
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all logs to file
    
    # Clear any existing handlers
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Create file handler that overwrites the log each time
    log_handler = logging.FileHandler(log_file, mode='w')
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(log_formatter)
    
    # Console handler (use the passed-in level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(console_level)
    
    # Add handlers to logger
    root_logger.addHandler(log_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

def get_ignored_directories(base_dir, context="validation"):
    """
    Read relative directory paths from ignore file and convert to absolute paths.
    
    Args:
        base_dir: Base directory for resolving relative paths
        context: Either "validation" or "stacking" to determine which directories to ignore
        
    Returns:
        List of absolute directory paths to ignore
    """
    ignored_dirs = []
    
    # For stacking, use the empty STACKING_IGNORED_DIRECTORIES list
    if context == "stacking":
        for dir_name in config.STACKING_IGNORED_DIRECTORIES:
            abs_path = os.path.join(base_dir, dir_name)
            ignored_dirs.append(abs_path)
            print(f"Ignoring directory for stacking: {dir_name}")
        return ignored_dirs
        
    # For validation, read from the file
    ignore_file = Path("config/val_dir_ignore.txt")
    
    if ignore_file.exists():
        with open(ignore_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('//') and not line.startswith('#'):
                    # Convert relative path to absolute
                    abs_path = os.path.join(base_dir, line)
                    ignored_dirs.append(abs_path)
                    print(f"Ignoring directory for validation: {line}")
    
    return ignored_dirs

def find_markdown_files(base_dir, recursive=config.RECURSIVE_SEARCH, context="validation"):
    """
    Find all markdown files in the directory (and subdirectories if recursive).
    
    Args:
        base_dir: Base directory to search
        recursive: Whether to search recursively
        context: Either "validation" or "stacking" to determine which directories to ignore
    
    Returns:
        List of Path objects for markdown files
    """
    base_path = Path(base_dir).resolve()
    
    # Get ignored directories for this run - context-aware
    ignored_directories = [Path(d).resolve() for d in get_ignored_directories(base_dir, context)]
    
    markdown_files = []
    
    # Walk through directory structure
    if recursive:
        for root, dirs, files in os.walk(base_path):
            root_path = Path(root).resolve()
            
            # Skip ignored directories - compare path objects not strings
            should_skip = False
            for ignore_dir in ignored_directories:
                # Check if this directory is the ignored dir or is inside it
                if root_path == ignore_dir or root_path.is_relative_to(ignore_dir):
                    try:
                        # Print path relative to base directory
                        rel_path = root_path.relative_to(base_path)
                        print(f"Skipping ignored directory: {rel_path}")
                    except ValueError:
                        # Fallback if relative_to fails
                        print(f"Skipping ignored directory: {root_path.name}")
                    should_skip = True
                    break
            
            if should_skip:
                continue
                
            for file in files:
                if file.lower().endswith('.md'):
                    markdown_files.append(Path(os.path.join(root, file)))
    else:
        # Non-recursive search
        markdown_files.extend(base_path.glob('*.md'))
    
    return markdown_files

def get_ignored_reports():
    """Get list of report files that should be skipped during processing."""
    ignored_reports = []
    
    if os.path.exists(config.IGNORE_FILE):
        with open(config.IGNORE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                report = line.strip()
                if report and not report.startswith('#'):
                    ignored_reports.append(report)
    
    return ignored_reports

def ensure_directory_exists(directory_path):
    """Create directory if it doesn't exist."""
    os.makedirs(directory_path, exist_ok=True)
    return directory_path  # Return the path after creating it