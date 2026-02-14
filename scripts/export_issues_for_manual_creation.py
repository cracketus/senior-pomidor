#!/usr/bin/env python3
"""
Export MVP_GITHUB_ISSUES_COMPLETE.md as GITHUB_ISSUES_EXPORT.md for manual GitHub issue creation.

This generates a clean markdown file with all issue information formatted for copy-pasting into GitHub's UI.

Usage:
    python scripts/export_issues_for_manual_creation.py [--output FILENAME]

Output:
    Generates GITHUB_ISSUES_EXPORT.md with all issue details ready to copy-paste.
"""

import re
import sys
from pathlib import Path
from typing import Optional

class IssueExporter:
    """Export issues from MVP_GITHUB_ISSUES_COMPLETE.md to manual creation format."""
    
    def __init__(self, source_file: Path):
        self.source_file = source_file
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
    
    def read_source(self) -> str:
        """Read source markdown file."""
        with open(self.source_file, 'r') as f:
            return f.read()
    
    def extract_issues(self, content: str) -> list[tuple[str, str]]:
        """Extract issue header and content pairs."""
        # Pattern: # Issue N — Title (flexible whitespace, any separator)
        issue_pattern = r'^#\s+Issue\s+(\d+[a-z]?)\s+.+$'
        
        issues = []
        current_header = None
        current_content = []
        
        for line in content.split('\n'):
            if re.match(issue_pattern, line, re.IGNORECASE):
                # Save previous issue
                if current_header:
                    issues.append((current_header, '\n'.join(current_content)))
                current_header = line
                current_content = []
            else:
                if current_header:
                    current_content.append(line)
        
        # Don't forget last issue
        if current_header:
            issues.append((current_header, '\n'.join(current_content)))
        
        return issues
    
    def generate_export(self, issues: list[tuple[str, str]]) -> str:
        """Generate export markdown."""
        lines = [
            "# GitHub Issues Export - Stage 1 Complete Specification",
            "",
            "This file contains all 10 Stage 1 issues formatted for manual GitHub creation.",
            "",
            "## How to Use",
            "",
            "1. For each issue below, click **New Issue** on GitHub",
            "2. Copy the **Title** text",
            "3. Paste into GitHub's Title field",
            "4. Copy the **Body** text",
            "5. Paste into GitHub's Body/Description field",
            "6. Add labels: `stage-1`, `issue-N` (e.g., `issue-1`)",
            "7. Click **Submit new issue**",
            "",
            "---",
            "",
        ]
        
        for idx, (header, content) in enumerate(issues, 1):
            # Extract issue number and title
            # Pattern: # Issue N [separator] Title
            # We'll extract number first, then get everything after as title
            match = re.match(r'^#\s+Issue\s+(\d+[a-z]?)(.*)', header, re.IGNORECASE)
            if not match:
                continue
            
            issue_num = match.group(1)
            remainder = match.group(2).strip()
            
            # Remove leading non-alphabetic characters and separators
            # Split on first word character and take everything after that
            title_match = re.search(r'([A-Za-z0-9].*)', remainder)
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = remainder.strip()
            
            # Prepend TOMATO-N: prefix to title
            title_with_prefix = f"TOMATO-{issue_num}: {title}"
            
            # Parse content sections
            sections = self._parse_sections(content)
            
            # Generate issue block
            lines.append(f"## Issue {issue_num}: {title_with_prefix}")
            lines.append("")
            
            lines.append("### GitHub UI - Title Field")
            lines.append("```")
            lines.append(title_with_prefix)
            lines.append("```")
            lines.append("")
            
            lines.append("### GitHub UI - Body Field")
            lines.append("```markdown")
            lines.extend(self._format_body(sections))
            lines.append("```")
            lines.append("")
            
            lines.append("### Labels to Add")
            lines.append("- `stage-1`")
            lines.append(f"- `issue-{issue_num}`")
            if 'NEW' in title or 'new' in title.lower():
                lines.append("- `new-issue`")
            lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _parse_sections(self, content: str) -> dict[str, str]:
        """Parse markdown sections."""
        sections = {}
        section_pattern = r'^## (.+?)\s*\n(.+?)(?=^##|\Z)'
        
        for match in re.finditer(section_pattern, content, re.MULTILINE | re.DOTALL):
            section_name = match.group(1).strip()
            section_content = match.group(2).strip()
            sections[section_name] = section_content
        
        return sections
    
    def _format_body(self, sections: dict[str, str]) -> list[str]:
        """Format sections as issue body."""
        body = []
        
        section_order = [
            'Context / Why',
            'Scope',
            'Non-goals',
            'Acceptance Criteria',
            'Required Tests',
            'Definition of Done',
            'Dependencies',
        ]
        
        for section_name in section_order:
            if section_name in sections:
                body.append(f"## {section_name}")
                body.append("")
                body.append(sections[section_name])
                body.append("")
        
        return body
    
    def export(self, output_file: Optional[Path] = None) -> Path:
        """Export to file."""
        if output_file is None:
            output_file = self.source_file.parent / "GITHUB_ISSUES_EXPORT.md"
        
        content = self.read_source()
        issues = self.extract_issues(content)
        export_content = self.generate_export(issues)
        
        with open(output_file, 'w') as f:
            f.write(export_content)
        
        print(f"✓ Exported {len(issues)} issues to: {output_file}")
        return output_file

def main():
    """Main entry point."""
    source_file = Path(__file__).parent.parent / "MVP_GITHUB_ISSUES_COMPLETE.md"
    output_file = Path(__file__).parent.parent / "GITHUB_ISSUES_EXPORT.md"
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_file = Path(sys.argv[idx + 1])
    
    try:
        exporter = IssueExporter(source_file)
        result = exporter.export(output_file)
        print(f"✓ Done! Open {result} to copy-paste issues into GitHub UI")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
