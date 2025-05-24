#!/usr/bin/env python3
"""
Convert Word documents (.docx) to Markdown (.md) files with line spacing cleanup.
"""
import os
import re
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

def clean_markdown_spacing(content):
    """
    Clean up excessive line spacing in markdown content.
    Limits vertical spacing to maximum of one blank line (two newlines total).
    """
    # Normalize line endings to \n (handles \r\n, \r, or \n)
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Replace any sequence of 3 or more newlines with exactly 2 newlines
    # This gives us a maximum of one blank line between content
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Clean up any trailing whitespace on lines
    lines = content.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]
    content = '\n'.join(cleaned_lines)
    
    return content

def convert_docx_to_markdown():
    """Convert all .docx files to markdown with line spacing cleanup"""
    
    # Import after potential installation
    import pypandoc
    
    # Get directories relative to script location
    helper_dir = Path(__file__).parent.absolute()
    source_folder = helper_dir / "_h_INPUT"
    output_folder = helper_dir / "_h_OUTPUT"
    
    # Create directories if they don't exist
    source_folder.mkdir(exist_ok=True)
    output_folder.mkdir(exist_ok=True)
    
    # Find all .docx files
    docx_files = list(source_folder.glob('*.docx'))
    
    if not docx_files:
        print(f"No .docx files found in {source_folder}")
        return
    
    print(f"Found {len(docx_files)} Word documents to convert")
    print("Will clean up excessive line spacing during conversion")
    
    # Track results
    converted_count = 0
    error_count = 0
    
    # Convert each file
    for docx_file in docx_files:
        try:
            # Create output filename (replace .docx with .md)
            md_filename = docx_file.stem + '.md'
            output_path = output_folder / md_filename
            
            # Convert using pypandoc to string first (not directly to file)
            markdown_content = pypandoc.convert_file(
                str(docx_file), 
                'markdown',
                extra_args=['--wrap=none', '--extract-media=.']
            )
            
            # Clean up the line spacing
            cleaned_content = clean_markdown_spacing(markdown_content)
            
            # Write the cleaned content to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"✓ Converted & cleaned: {docx_file.name} → {md_filename}")
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
        print("Line spacing has been normalized (max 1 blank line between sections)")

def check_pandoc():
    """Check if pandoc is installed system-wide"""
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

if __name__ == "__main__":
    print("Word to Markdown Converter with Line Cleanup")
    print("=" * 50)
    
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