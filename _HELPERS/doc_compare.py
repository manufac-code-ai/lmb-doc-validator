import os
import re
from pathlib import Path
from datetime import datetime

# ========================================
# CONFIGURATION - Adjust these settings
# ========================================

# Display Controls
SHOW_EXACT_MATCHES = False      # Set to True to show exact matches in the log
SHOW_PATHS = True              # Set to True to show full file paths instead of just filenames

# Fuzzy Matching Thresholds
TEXT_SIMILARITY_THRESHOLD = 0.4  # Minimum text similarity for fuzzy matching (default: 0.6)
SUBSTRING_MATCH_SCORE = 0.8     # Score for when one filename contains the other (default: 0.8)
SHARED_NUMBERS_BONUS = 0.1      # Bonus points when filenames share numbers (default: 0.1)
MIN_SHARED_NUMBERS_FOR_BONUS = 1  # Minimum shared numbers to earn bonus (default: 1)
MINIMUM_MATCH_SCORE = 0.8       # Minimum score to consider a match (default: 0.7)

# Match Type Scores
DATE_POSITION_SWAP_SCORE = 0.99  # Score for date position swaps (default: 0.99)
EXACT_MATCH_SCORE = 1.0         # Score for exact matches (default: 1.0)
FOLLOW_UP_SCORE = 0.6           # Score for follow-up pattern matches (default: 0.6)

# ========================================

def clean_filename(filename):
    """Clean filename for comparison by removing extensions and normalizing"""
    # Remove file extension
    name = os.path.splitext(filename)[0]
    # Convert to lowercase and replace common separators with spaces
    name = re.sub(r'[-_\.]', ' ', name.lower())
    # Remove extra whitespace
    name = ' '.join(name.split())
    return name

def extract_numbers(filename):
    """Extract all numbers from filename for comparison"""
    return set(re.findall(r'\d+', filename))

def extract_date_from_filename(filename):
    """Extract 6-digit date string from filename (leading or trailing)."""
    name_no_ext = os.path.splitext(filename)[0]
    
    # Try leading: "230103 Client Report"
    leading_match = re.match(r'^(\d{6})\s+(.+)', name_no_ext)
    if leading_match:
        return leading_match.group(1), leading_match.group(2)
    
    # Try trailing: "Client Report 230103"
    trailing_match = re.search(r'^(.+)\s+(\d{6})$', name_no_ext)
    if trailing_match:
        return trailing_match.group(2), trailing_match.group(1)
    
    return None, name_no_ext

def get_file_lists():
    """Get lists of newer and legacy files using actual directory paths"""
    
    # Define paths
    newer_base = "/Users/stevenbrown/Library/Mobile Documents/com~apple~CloudDocs/Documents_SRB iCloud/Projects/SOFTWARE dev SUPPORT projects/Ai MASTER CONTROL/Ai Projects, Effort/Ai_pj - sb_Dv_Service_Reports/jobGPT - convert sb svc rpts to js experience for res/gpt pj - rpts2resume 1 collect reports"
    
    legacy_base = "/Users/stevenbrown/Documents_SRB (local)/DIVERSIFIED FILES srb/Dv 1 - FST/Dv FST 3 - Service Tickets"
    
    # Collect newer files
    newer_files = []
    newer_path = Path(newer_base)
    
    # Look in main folder and subfolders
    for folder_name in ['250523 srb Service Reports master', '250523 srb Service Reports master OTHER']:
        folder_path = newer_path / folder_name
        if folder_path.exists():
            # Recursively find all .md files
            for md_file in folder_path.rglob('*.md'):
                newer_files.append(str(md_file.relative_to(newer_path)))
    
    # Collect legacy files
    legacy_files = []
    legacy_path = Path(legacy_base)
    
    if legacy_path.exists():
        # Target file extensions
        target_extensions = {'.docx', '.doc', '.txt', '.md'}
        
        # Recursively find all target files
        for file_path in legacy_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in target_extensions:
                legacy_files.append(str(file_path.relative_to(legacy_path)))
    
    return newer_files, legacy_files

def load_skip_list(skip_file="doc_compare_skip.txt"):
    """Load list of already-reviewed matches to skip"""
    skip_pairs = set()
    
    # Get the script's directory and look for skip file there
    script_dir = Path(__file__).parent.absolute()
    skip_file_path = script_dir / skip_file
    
    try:
        with open(skip_file_path, 'r') as f:
            for line in f:
                if '|' in line and not line.startswith('#'):
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        newer = parts[0].strip()
                        legacy = parts[1].strip()
                        skip_pairs.add((newer, legacy))
        print(f"DEBUG: Loaded {len(skip_pairs)} skip pairs from {skip_file_path}")
        for pair in list(skip_pairs)[:3]:  # Show first 3
            print(f"DEBUG: Skip pair: '{pair[0]}' | '{pair[1]}'")
    except FileNotFoundError:
        print(f"DEBUG: Skip file not found at {skip_file_path}")
    return skip_pairs

def find_matches(newer_files, legacy_files):
    """Find matches using stable global optimization"""
    skip_pairs = load_skip_list()
    
    # Build all possible match scores first
    all_potential_matches = []
    
    for i, newer_file in enumerate(newer_files):
        newer_name = os.path.basename(newer_file)
        newer_clean = clean_filename(newer_name)
        newer_numbers = extract_numbers(newer_name)
        newer_date, newer_name_part = extract_date_from_filename(newer_name)
        
        for j, legacy_file in enumerate(legacy_files):
            legacy_name = os.path.basename(legacy_file)
            
            # Skip if in skip list
            if (newer_name, legacy_name) in skip_pairs:
                continue
                
            legacy_clean = clean_filename(legacy_name)
            legacy_numbers = extract_numbers(legacy_name)
            legacy_date, legacy_name_part = extract_date_from_filename(legacy_name)
            
            # Calculate match score
            score = 0.0
            match_type = None
            
            # Date-position swap (highest priority)
            if newer_date and legacy_date == newer_date:
                if newer_name_part.lower().strip() == legacy_name_part.lower().strip():
                    score = DATE_POSITION_SWAP_SCORE
                    match_type = 'date_position_swap'
            
            # Exact filename match
            elif newer_clean == legacy_clean:
                score = EXACT_MATCH_SCORE
                match_type = 'exact'
            
            # PRIMARY: Text similarity (substring matching)
            elif newer_clean in legacy_clean or legacy_clean in newer_clean:
                score = SUBSTRING_MATCH_SCORE
                match_type = 'potential'

            # SECONDARY: Fuzzy text similarity with shared numbers as bonus
            else:
                from difflib import SequenceMatcher
                text_similarity = SequenceMatcher(None, newer_clean, legacy_clean).ratio()
                
                # Base score from text similarity
                if text_similarity >= TEXT_SIMILARITY_THRESHOLD:
                    score = text_similarity
                    
                    # Bonus for shared numbers (but not required)
                    shared_numbers = newer_numbers.intersection(legacy_numbers)
                    if len(shared_numbers) >= MIN_SHARED_NUMBERS_FOR_BONUS:
                        score += SHARED_NUMBERS_BONUS
                        
                    # Cap at 100% confidence
                    score = min(score, 1.0)
                
                match_type = 'potential'
            
            # Follow-up pattern
            if score == 0.0 and ('follow' in newer_clean and any(word in legacy_clean for word in newer_clean.split() if word != 'follow')):
                score = FOLLOW_UP_SCORE
                match_type = 'follow_up'
            
            # Only keep matches above threshold
            if score >= MINIMUM_MATCH_SCORE:
                all_potential_matches.append({
                    'newer_idx': i,
                    'legacy_idx': j,
                    'newer_file': newer_file,
                    'legacy_file': legacy_file,
                    'score': score,
                    'match_type': match_type
                })
    
    # Sort by score (highest first) for greedy optimization
    all_potential_matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Greedy assignment (stable and deterministic)
    used_newer = set()
    used_legacy = set()
    final_matches = {
        'exact': [],
        'potential': [],
        'follow_up': []
    }
    
    for match in all_potential_matches:
        newer_idx = match['newer_idx']
        legacy_idx = match['legacy_idx']
        
        # Skip if already assigned
        if newer_idx in used_newer or legacy_idx in used_legacy:
            continue
        
        # Assign this match
        used_newer.add(newer_idx)
        used_legacy.add(legacy_idx)
        
        # Categorize by match type
        if match['match_type'] in ['exact', 'date_position_swap']:
            final_matches['exact'].append({
                'newer': match['newer_file'],
                'legacy': match['legacy_file'],
                'confidence': match['score']
            })
        elif match['match_type'] == 'potential':
            final_matches['potential'].append({
                'newer': match['newer_file'],
                'legacy': match['legacy_file'],
                'confidence': match['score']
            })
        elif match['match_type'] == 'follow_up':
            final_matches['follow_up'].append({
                'newer': match['newer_file'],
                'legacy': match['legacy_file'],
                'confidence': match['score']
            })
    
    # Find unmatched files
    final_matches['newer_unmatched'] = [newer_files[i] for i in range(len(newer_files)) if i not in used_newer]
    final_matches['legacy_unmatched'] = [legacy_files[i] for i in range(len(legacy_files)) if i not in used_legacy]
    
    return final_matches

def generate_report(matches, newer_count, legacy_count):
    """Generate a detailed report of the matching results"""
    
    # Get base directories for path display
    newer_base_dir = "/Users/stevenbrown/Library/Mobile Documents/com~apple~CloudDocs/Documents_SRB iCloud/Projects/SOFTWARE dev SUPPORT projects/Ai MASTER CONTROL/Ai Projects, Effort/Ai_pj - sb_Dv_Service_Reports/jobGPT - convert sb svc rpts to js experience for res/gpt pj - rpts2resume 1 collect reports"
    legacy_base_dir = "/Users/stevenbrown/Documents_SRB (local)/DIVERSIFIED FILES srb/Dv 1 - FST/Dv FST 3 - Service Tickets"
    
    report_lines = []
    report_lines.append("# File Matching Report")
    report_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    report_lines.append("")
    
    # Summary
    report_lines.append("## Summary")
    report_lines.append(f"- **Newer files scanned**: {newer_count}")
    report_lines.append(f"- **Legacy files scanned**: {legacy_count}")
    report_lines.append(f"- **Exact matches**: {len(matches['exact'])}")
    report_lines.append(f"- **Potential matches**: {len(matches['potential'])}")
    report_lines.append(f"- **Follow-up variants**: {len(matches['follow_up'])}")
    report_lines.append(f"- **Newer files unmatched**: {len(matches['newer_unmatched'])}")
    report_lines.append(f"- **Legacy files unmatched**: {len(matches['legacy_unmatched'])}")
    report_lines.append("")
    
    # Show exact matches only if requested
    if SHOW_EXACT_MATCHES and matches['exact']:
        report_lines.append("## Exact Matches")
        report_lines.append("*Files with identical cleaned names*")
        report_lines.append("")
        for match in matches['exact']:
            report_lines.append(f"#### {os.path.basename(match['newer'])}")
            if SHOW_PATHS:
                report_lines.append(f"- Newer:\t`{match['newer']}`")
                report_lines.append(f"- Legacy:\t`{match['legacy']}`")
            else:
                report_lines.append(f"- Newer:\t`{os.path.basename(match['newer'])}`")
                report_lines.append(f"- Legacy:\t`{os.path.basename(match['legacy'])}`")
            report_lines.append("")
    elif matches['exact']:
        report_lines.append("## Exact Matches")
        report_lines.append(f"*{len(matches['exact'])} exact matches found (hidden for brevity)*")
        report_lines.append("*Set show_exact_matches=True to display them*")
        report_lines.append("")
    
    # Potential matches
    if matches['potential']:
        report_lines.append("## Potential Matches")
        report_lines.append("*Files with high similarity or shared identifiers*")
        report_lines.append("")
        for match in matches['potential']:
            report_lines.append(f"#### {os.path.basename(match['newer'])}")
            if SHOW_PATHS:
                # Show paths with base directory for context
                newer_path = os.path.join(newer_base_dir, match['newer'])
                legacy_path = os.path.join(legacy_base_dir, match['legacy'])
                report_lines.append(f"- Newer:\t`{newer_path}`")
                report_lines.append(f"- Legacy:\t`{legacy_path}`")
            else:
                # Just show filenames
                report_lines.append(f"- Newer:\t`{os.path.basename(match['newer'])}`")
                report_lines.append(f"- Legacy:\t`{os.path.basename(match['legacy'])}`")
            report_lines.append(f"- **Confidence**: {match['confidence']:.1%}")
            report_lines.append("")
    
    # Follow-up variants
    if matches['follow_up']:
        report_lines.append("## Follow-up Variants")
        report_lines.append("*Detected follow-up or variant files*")
        report_lines.append("")
        for match in matches['follow_up']:
            report_lines.append(f"#### {os.path.basename(match['newer'])}")
            if SHOW_PATHS:
                report_lines.append(f"- Newer:\t`{match['newer']}`")
                report_lines.append(f"- Legacy:\t`{match['legacy']}`")
            else:
                report_lines.append(f"- Newer:\t`{os.path.basename(match['newer'])}`")
                report_lines.append(f"- Legacy:\t`{os.path.basename(match['legacy'])}`")
            report_lines.append("")
    
    # Unmatched newer files
    if matches['newer_unmatched']:
        report_lines.append("## Unmatched Newer Files")
        report_lines.append("*Newer files without clear legacy counterparts*")
        report_lines.append("")
        for file in matches['newer_unmatched']:
            if SHOW_PATHS:
                report_lines.append(f"- `{file}`")
            else:
                report_lines.append(f"- `{os.path.basename(file)}`")
        report_lines.append("")
    
    # Sample of unmatched legacy files (limit to avoid overwhelming output)
    if matches['legacy_unmatched']:
        report_lines.append("## Unmatched Legacy Files")
        report_lines.append(f"*{len(matches['legacy_unmatched'])} legacy files without newer counterparts*")
        report_lines.append("")
        
        # Show first 20 as examples
        sample_size = min(20, len(matches['legacy_unmatched']))
        report_lines.append(f"*Showing first {sample_size} as examples:*")
        report_lines.append("")
        
        for file in matches['legacy_unmatched'][:sample_size]:
            if SHOW_PATHS:
                report_lines.append(f"- `{file}`")
            else:
                report_lines.append(f"- `{os.path.basename(file)}`")
        
        if len(matches['legacy_unmatched']) > sample_size:
            report_lines.append(f"- ... and {len(matches['legacy_unmatched']) - sample_size} more")
        report_lines.append("")
    
    return "\n".join(report_lines)

def main():
    """Main execution function"""
    
    print("File Matching Analysis")
    print("=" * 50)
    
    # Get file lists
    newer_files, legacy_files = get_file_lists()
    
    print(f"Found {len(newer_files)} newer markdown files")
    print(f"Found {len(legacy_files)} legacy files (.docx, .doc, .txt, .md)")
    
    if not newer_files or not legacy_files:
        print("⚠️  No files found to compare. Check your directory structure.")
        return
    
    # Find matches 
    print("Analyzing matches...")
    matches = find_matches(newer_files, legacy_files)
    
    # Generate and save report
    print("Generating report...")
    report = generate_report(matches, len(newer_files), len(legacy_files))
    
    # Save report to _h_LOGS directory
    script_dir = Path(__file__).parent.absolute()
    logs_dir = script_dir / "_h_LOGS"
    logs_dir.mkdir(exist_ok=True)  # Create directory if it doesn't exist
    
    report_file = logs_dir / "zz_match_log.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report written to: {report_file}")
    print(f"Found {len(matches['exact'])} exact matches, {len(matches['potential'])} potential matches, {len(matches['follow_up'])} follow-up variants")

if __name__ == "__main__":
    main()