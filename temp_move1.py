#!/usr/bin/env python3
"""
Move non-report files from source folder based on filenames in the 'not reports' folder.
"""
import os
import shutil
from pathlib import Path

def move_non_reports():
    """Move files from source to temp folder based on identified non-reports"""
    
    # Define paths
    # source_folder = Path('/Users/stevenbrown/Library/Mobile Documents/com~apple~CloudDocs/Documents_SRB iCloud/Projects/SOFTWARE dev SUPPORT projects/Ai MASTER CONTROL/Ai Projects, Effort/Ai_pj - sb_Dv_Service_Reports/jobGPT - convert sb svc rpts to js experience for res/gpt pj - rpts2resume 1 collect reports/230621 reports copied from ssq')
    source_folder = Path('/Users/stevenbrown/Library/Mobile Documents/com~apple~CloudDocs/Documents_SRB iCloud/Projects/SOFTWARE dev SUPPORT projects/Ai MASTER CONTROL/Ai Projects, Effort/Ai_pj - sb_Dv_Service_Reports/jobGPT - convert sb svc rpts to js experience for res/gpt pj - rpts2resume 1 collect reports/230621 reports copied from ssq OTHER/PM (from invalid out)')
    
    not_reports_folder = Path('_out/validated/1 not reports')
    destination_folder = Path('_out/_temp_OUT')
    
    # Create destination folder if it doesn't exist
    destination_folder.mkdir(parents=True, exist_ok=True)
    
    # Get list of non-report filenames
    if not not_reports_folder.exists():
        print(f"Error: '{not_reports_folder}' folder not found!")
        return
    
    non_report_files = []
    for file in not_reports_folder.iterdir():
        if file.is_file() and file.suffix.lower() == '.md':
            non_report_files.append(file.name)
    
    print(f"Found {len(non_report_files)} non-report files to identify in source")
    
    # Track results
    moved_count = 0
    not_found_count = 0
    error_count = 0
    
    # Search source folder (including subdirectories) and move matching files
    for non_report_name in non_report_files:
        found = False
        
        # Search recursively through source folder
        for root, dirs, files in os.walk(source_folder):
            if non_report_name in files:
                source_file_path = Path(root) / non_report_name
                destination_file_path = destination_folder / non_report_name
                
                try:
                    # Move the file
                    shutil.move(str(source_file_path), str(destination_file_path))
                    print(f"✓ Moved: {non_report_name}")
                    moved_count += 1
                    found = True
                    break
                except Exception as e:
                    print(f"✗ Error moving {non_report_name}: {e}")
                    error_count += 1
                    found = True
                    break
        
        if not found:
            print(f"✗ Not found in source: {non_report_name}")
            not_found_count += 1
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Files successfully moved: {moved_count}")
    print(f"Files not found in source: {not_found_count}")
    print(f"Errors during move: {error_count}")
    print(f"Total files processed: {len(non_report_files)}")
    
    if moved_count > 0:
        print(f"\nMoved files are now in: {destination_folder}")

if __name__ == "__main__":
    print("Moving non-report files from source folder...")
    move_non_reports()
    print("Done!")