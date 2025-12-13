import diff_match_patch as dmp_module
from typing import List, Tuple

def generate_unified_diff(original: str, fixed: str, context_lines: int = 3) -> str:
    """
    Generate a unified diff between original and fixed YAML content.
    
    Args:
        original: Original YAML content
        fixed: Fixed YAML content
        context_lines: Number of context lines to include
        
    Returns:
        Unified diff string with comments
    """
    dmp = dmp_module.diff_match_patch()
    
    # Create diffs
    diffs = dmp.diff_main(original, fixed)
    dmp.diff_cleanupSemantic(diffs)
    
    # Convert to patch
    patches = dmp.patch_make(original, diffs)
    patch_text = dmp.patch_toText(patches)
    
    # Format as unified diff
    lines_original = original.split('\n')
    lines_fixed = fixed.split('\n')
    
    diff_lines = []
    diff_lines.append("--- original.yml")
    diff_lines.append("+++ fixed.yml")
    
    # Simple line-by-line comparison
    max_lines = max(len(lines_original), len(lines_fixed))
    i = 0
    
    while i < max_lines:
        orig_line = lines_original[i] if i < len(lines_original) else None
        fixed_line = lines_fixed[i] if i < len(lines_fixed) else None
        
        if orig_line != fixed_line:
            # Start a hunk
            diff_lines.append(f"@@ -{i+1},{context_lines*2+1} +{i+1},{context_lines*2+1} @@")
            
            # Add context before
            for j in range(max(0, i-context_lines), i):
                if j < len(lines_original):
                    diff_lines.append(f" {lines_original[j]}")
            
            # Add the change
            if orig_line is not None:
                diff_lines.append(f"-{orig_line}")
            if fixed_line is not None:
                diff_lines.append(f"+{fixed_line}")
            
            # Add context after
            for j in range(i+1, min(len(lines_original), i+context_lines+1)):
                diff_lines.append(f" {lines_original[j]}")
        
        i += 1
    
    return '\n'.join(diff_lines)

def add_explanatory_comments(diff: str, vulnerability_type: str) -> str:
    """
    Add explanatory comments to a diff based on vulnerability type.
    
    Args:
        diff: Unified diff string
        vulnerability_type: Type of vulnerability being fixed
        
    Returns:
        Diff with explanatory comments
    """
    comments = {
        "unpinned_action": "# FIX: Pinned action to specific commit SHA for security and reproducibility",
        "excessive_permissions": "# FIX: Added minimal required permissions to follow least privilege principle",
        "hardcoded_secret": "# FIX: Replaced hardcoded secret with GitHub Secrets reference",
        "weak_hardening": "# FIX: Added security hardening measures"
    }
    
    comment = comments.get(vulnerability_type, "# FIX: Applied security fix")
    return f"{comment}\n{diff}"

def format_diff_with_line_numbers(diff: str) -> str:
    """
    Format diff with line numbers for better readability.
    
    Args:
        diff: Unified diff string
        
    Returns:
        Formatted diff with line numbers
    """
    lines = diff.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines, 1):
        if line.startswith('@@'):
            formatted_lines.append(f"\n{line}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)
