#!/usr/bin/env python3
"""
Convert Word documents (.docx) to Markdown (.md) files.
"""
import os
from pathlib import Path
import subprocess
import sys

def install_pandoc_python():
    """Install required package if not available"""
    try:
        import pypandoc
        return True
    except ImportError:
        print("Installing pypandoc...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypandoc"])
        import pypandoc
        return True

def convert_docx_to_markdown():
    """Convert all .docx files to markdown"""
    
    # Import after potential installation
    import pypandoc
    
    # Define paths
    source_folder = Path('/Users/stevenbrown/Library/Mobile Documents/com~apple~CloudDocs/Documents_SRB iCloud/Projects/SOFTWARE dev SUPPORT projects/Ai MASTER CONTROL/Ai Projects, Effort/Ai_pj - sb_Dv_Service_Reports/jobGPT - convert sb svc rpts to js experience for res/gpt pj - rpts2resume 1 collect reports/docx')
    
    output_folder = Path('/Users/stevenbrown/Library/Mobile Documents/com~apple~CloudDocs/Documents_SRB iCloud/Projects/SOFTWARE dev SUPPORT projects/Ai MASTER CONTROL/Ai Projects, Effort/Ai_pj - sb_Dv_Service_Reports/jobGPT - convert sb svc rpts to js experience for res/gpt pj - rpts2resume 1 collect reports/docx_OUT')
    
    # Create output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Find all .docx files
    docx_files = list(source_folder.glob('*.docx'))
    
    if not docx_files:
        print(f"No .docx files found in {source_folder}")
        return
    
    print(f"Found {len(docx_files)} Word documents to convert")
    
    # Track results
    converted_count = 0
    error_count = 0
    
    # Convert each file
    for docx_file in docx_files:
        try:
            # Create output filename (replace .docx with .md)
            md_filename = docx_file.stem + '.md'
            output_path = output_folder / md_filename
            
            # Convert using pypandoc
            output = pypandoc.convert_file(
                str(docx_file), 
                'markdown',
                outputfile=str(output_path),
                extra_args=['--wrap=none', '--extract-media=.']
            )
            
            print(f"✓ Converted: {docx_file.name} → {md_filename}")
            converted_count += 1
            
        except Exception as e:
            print(f"✗ Error converting {docx_file.name}: {e}")
            error_count += 1
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Files successfully converted: {converted_count}")
    print(f"Conversion errors: {error_count}")
    print(f"Total files processed: {len(docx_files)}")
    
    if converted_count > 0:
        print(f"\nConverted files are in: {output_folder}")

def check_pandoc():
    """Check if pandoc is installed system-wide"""
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

if __name__ == "__main__":
    print("Word to Markdown Converter")
    print("=" * 40)
    
    # Check for pandoc
    if not check_pandoc():
        print("Warning: Pandoc not found system-wide.")
        print("pypandoc will try to download its own copy.")
    
    # Install/import pypandoc
    if install_pandoc_python():
        print("Starting conversion...")
        convert_docx_to_markdown()
        print("Done!")
    else:
        print("Failed to install required packages.")