#!/usr/bin/env python3
"""
Export MVP_GITHUB_ISSUES_COMPLETE.md as GITHUB_ISSUES_EXPORT.md.

Generates a markdown file with all issue information formatted for manual
copy-paste into GitHub's UI.

Usage:
    python scripts/export_issues_for_manual_creation.py [--output FILENAME]

Output:
    Writes GITHUB_ISSUES_EXPORT.md by default in the repository root.
"""

import re
import sys
from pathlib import Path
from typing import Optional


class IssueExporter:
    """Export issues from MVP_GITHUB_ISSUES_COMPLETE.md to manual format."""

    def __init__(self, source_file: Path):
        self.source_file = source_file
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")

    def read_source(self) -> str:
        """Read source markdown file."""
        with open(self.source_file, "r", encoding="utf-8") as f:
            return f.read()

    def extract_issues(self, content: str) -> list[tuple[str, str]]:
        """Extract issue header and content pairs."""
        issue_pattern = r"^#\s+Issue\s+(\d+[a-z]?)\s+.+$"

        issues = []
        current_header = None
        current_content = []

        for line in content.split("\n"):
            if re.match(issue_pattern, line, re.IGNORECASE):
                if current_header:
                    issues.append((current_header, "\n".join(current_content)))
                current_header = line
                current_content = []
            else:
                if current_header:
                    current_content.append(line)

        if current_header:
            issues.append((current_header, "\n".join(current_content)))

        return issues

    def generate_export(self, issues: list[tuple[str, str]]) -> str:
        """Generate export markdown for all issues."""
        lines = [
            "# GitHub Issues Export - Stage 1 Complete Specification",
            "",
            "This file contains all Stage 1 issues formatted for manual creation.",
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
            match = re.match(r"^#\s+Issue\s+(\d+[a-z]?)(.*)", header, re.IGNORECASE)
            if not match:
                continue

            issue_num = match.group(1)
            remainder = match.group(2).strip()

            title_match = re.search(r"([A-Za-z0-9].*)", remainder)
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = remainder.strip()

            title_with_prefix = f"TOMATO-{issue_num}: {title}"

            sections = self._parse_sections(content)

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
            if "NEW" in title or "new" in title.lower():
                lines.append("- `new-issue`")
            lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _parse_sections(self, content: str) -> dict[str, str]:
        """Parse markdown sections into a dict."""
        sections = {}
        section_pattern = r"^## (.+?)\s*\n(.+?)(?=^##|\Z)"

        for match in re.finditer(section_pattern, content, re.MULTILINE | re.DOTALL):
            section_name = match.group(1).strip()
            section_content = match.group(2).strip()
            sections[section_name] = section_content

        return sections

    def _format_body(self, sections: dict[str, str]) -> list[str]:
        """Format the sections into a list of markdown lines for the body."""
        body = []

        section_order = [
            "Context / Why",
            "Scope",
            "Non-goals",
            "Acceptance Criteria",
            "Required Tests",
            "Definition of Done",
            "Dependencies",
        ]

        for section_name in section_order:
            if section_name in sections:
                body.append(f"## {section_name}")
                body.append("")
                body.append(sections[section_name])
                body.append("")

        return body

    def export(self, output_file: Optional[Path] = None) -> Path:
        """Export issues to a file and return the output path."""
        if output_file is None:
            output_file = self.source_file.parent / "GITHUB_ISSUES_EXPORT.md"

        content = self.read_source()
        issues = self.extract_issues(content)
        export_content = self.generate_export(issues)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(export_content)

        print(f"✓ Exported {len(issues)} issues to: {output_file}")
        return output_file


def main() -> int:
    source_file = Path(__file__).parent.parent / "MVP_GITHUB_ISSUES_COMPLETE.md"
    output_file = Path(__file__).parent.parent / "GITHUB_ISSUES_EXPORT.md"

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
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


if __name__ == "__main__":
    sys.exit(main())
