#!/usr/bin/env python3
"""
Rename files with trailing 6-digit dates to leading 6-digit dates.
Example: "Mentor - A103A Big Muddy3 230103.md" → "230103 Mentor - A103A Big Muddy3.md"
"""

import os
import shutil
import re
from pathlib import Path

def main():
    # Get directories relative to script location
    helper_dir = Path(__file__).parent.absolute()
    source_dir = helper_dir / "_h_INPUT"
    output_dir = helper_dir / "_h_OUTPUT"
    
    # Create directories if they don't exist
    source_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Pattern to match files ending with " YYMMDD.md"
    # Matches: space + 6 digits + .md at end of filename
    date_pattern = r'^(.+)\s(\d{6})\.md$'
    
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    if not source_path.exists():
        print(f"Error: Source directory does not exist: {source_dir}")
        return
    
    processed_count = 0
    skipped_count = 0
    
    print(f"Processing files from: {source_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 80)
    
    # Process all .md files in source directory
    for file_path in source_path.glob('*.md'):
        filename = file_path.name
        
        # Check if filename matches the pattern
        match = re.match(date_pattern, filename)
        
        if match:
            # Extract the base name and date
            base_name = match.group(1)
            date_string = match.group(2)
            
            # Create new filename: date + space + base_name + .md
            new_filename = f"{date_string} {base_name}.md"
            
            # Source and destination paths
            source_file = file_path
            dest_file = output_path / new_filename
            
            # Copy file with new name
            try:
                shutil.copy2(source_file, dest_file)
                print(f"✅ {filename}")
                print(f"   → {new_filename}")
                processed_count += 1
            except Exception as e:
                print(f"❌ Error copying {filename}: {e}")
        else:
            print(f"⚠️  Skipped (no trailing date): {filename}")
            skipped_count += 1
    
    print("-" * 80)
    print(f"Processing complete!")
    print(f"Files processed: {processed_count}")
    print(f"Files skipped: {skipped_count}")
    print(f"Total files examined: {processed_count + skipped_count}")

if __name__ == "__main__":
    main()