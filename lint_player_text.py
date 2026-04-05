#!/usr/bin/env python3
"""Scans player-facing text in local Python files for internal/dev language that shouldn't be shown to players."""

import re
import sys
from pathlib import Path

BANNED_PATTERNS = [
    ("continuation target", "use 'who to continue as' or similar"),
    ("continuation candidate", "use 'available lives' or 'family members'"),
    ("connected actor", "use 'family' or 'family member'"),
    ("linked actor", "use 'family' or 'family member'"),
    ("focused actor", "use the character name or 'you'"),
    ("structural_status", "internal field — don't display"),
    ("record_type", "internal field — don't display"),
    ("link_type", "internal field — don't display"),
    ("link_role", "internal field — don't display"),
    ("bootstrap", "internal term — don't display"),
    ("actor_entry", "internal record type — don't display"),
    ("family_bootstrap", "internal record type — don't display"),
    ("entity_id", "internal field — don't display"),
    ("source_id", "internal field — don't display"),
    ("target_id", "internal field — don't display"),
    ("World Body", "use 'Planet' on Earth"),
    ("Jurisdiction", "use 'Country' on Earth"),
    ("Death Interrupt", "use 'Death'"),
]

# Patterns that indicate player-facing text (string literals in display contexts)
DISPLAY_CONTEXTS = [
    r'center_text\("([^"]+)"',
    r'last_message = "([^"]+)"',
    r'lines\.append\("([^"]+)"\)',
    r'right_lines\.append\("([^"]+)"\)',
    r'f"([^"]*)"',
]


def scan_file(filepath):
    issues = []
    with open(filepath) as f:
        for line_num, line in enumerate(f, 1):
            # Skip comments and non-display code
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("def ") or stripped.startswith("class "):
                continue

            # Only check lines that look like they contain player-facing strings
            if not any(marker in line for marker in ['center_text', 'last_message', 'lines.append', 'f"', "f'"]):
                continue

            display_line = re.sub(r"\{[^}]*\}", "", line)
            literal_fragments = re.findall(r'"([^"]*)"|\'([^\']*)\'', display_line)
            literal_text = " ".join(fragment for pair in literal_fragments for fragment in pair if fragment)
            for pattern, suggestion in BANNED_PATTERNS:
                if pattern.lower() in literal_text.lower():
                    issues.append((line_num, pattern, suggestion, stripped[:80]))

    return issues


def main():
    filepaths = [Path(arg) for arg in sys.argv[1:]] if len(sys.argv) > 1 else sorted(Path(".").glob("*.py"))
    all_issues = []

    for filepath in filepaths:
        issues = scan_file(filepath)
        for line_num, pattern, suggestion, context in issues:
            all_issues.append((filepath, line_num, pattern, suggestion, context))

    if all_issues:
        print(f"FOUND {len(all_issues)} potential player-facing text issues in {len(filepaths)} file(s):")
        for filepath, line_num, pattern, suggestion, context in all_issues:
            print(f"  {filepath}:L{line_num}: '{pattern}' — {suggestion}")
            print(f"    {context}")
        print()
        print("Note: some matches may be false positives (internal logic, not display text).")
        print("Review each match to confirm it's actually player-visible.")
        sys.exit(1)

    if len(sys.argv) > 1:
        print(f"No player-facing text issues found in {len(filepaths)} file(s).")
    else:
        print(f"No player-facing text issues found in {len(filepaths)} local Python files.")
    sys.exit(0)


if __name__ == "__main__":
    main()
