#!/usr/bin/env python3
"""
Parse MVP_GITHUB_ISSUES_COMPLETE.md and create GitHub issues via GitHub CLI.

Prerequisites:
- GitHub CLI installed: https://cli.github.com/
- Authenticated: run `gh auth login`
- In the repository directory: cd senior-pomidor

Usage:
    python scripts/create_github_issues.py [--dry-run] [--token YOUR_TOKEN]

Options:
    --dry-run    Print issues without creating them
    --token      GitHub token (uses gh CLI auth if not provided)
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


# Color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def read_issues_file() -> str:
    """Read the MVP_GITHUB_ISSUES_COMPLETE.md file."""
    file_path = Path(__file__).parent.parent / "MVP_GITHUB_ISSUES_COMPLETE.md"
    if not file_path.exists():
        print(f"{Colors.RED}Error: {file_path} not found{Colors.END}")
        sys.exit(1)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_issues(content: str) -> list[dict]:
    """Extract issues from markdown content.

    Matches headers like: "# Issue 1 — Title"
    """
    issue_pattern = r"^#\s+Issue\s+(\d+[a-z]?)\s+(.+)$"
    issues = []

    current_issue = None
    current_block = []
    issue_number = None

    for line in content.split("\n"):
        match = re.match(issue_pattern, line, re.IGNORECASE)
        if match:
            if current_issue is not None:
                issues.append({
                    "issue_number": issue_number,
                    "header": current_issue,
                    "content": "\n".join(current_block),
                })
            issue_number = match.group(1)
            current_issue = match.group(2)
            current_block = []
        elif current_issue is not None:
            current_block.append(line)

    if current_issue is not None:
        issues.append({
            "issue_number": issue_number,
            "header": current_issue,
            "content": "\n".join(current_block),
        })

    return issues


def parse_issue_details(issue: dict) -> dict:
    """Parse issue markdown into structured data."""
    content = issue["content"]

    title_match = re.search(
        r"^## Title\s*\n(.+?)(?=\n##|\Z)", content, re.MULTILINE | re.DOTALL
    )
    title = title_match.group(1).strip() if title_match else issue["header"]

    sections = {}
    section_pattern = r"^## (.+?)\s*\n(.+?)(?=^##|\Z)"
    for match in re.finditer(section_pattern, content, re.MULTILINE | re.DOTALL):
        section_name = match.group(1).strip()
        section_content = match.group(2).strip()
        sections[section_name] = section_content

    return {
        "issue_number": issue["issue_number"],
        "title": title,
        "context": sections.get("Context / Why", ""),
        "scope": sections.get("Scope", ""),
        "non_goals": sections.get("Non-goals", ""),
        "acceptance_criteria": sections.get("Acceptance Criteria", ""),
        "required_tests": sections.get("Required Tests", ""),
        "definition_of_done": sections.get("Definition of Done", ""),
        "dependencies": sections.get("Dependencies", ""),
    }


def format_issue_body(details: dict) -> str:
    """Format parsed issue details into GitHub markdown body."""
    body_parts = []

    if details["context"]:
        body_parts.append(f"## Context / Why\n\n{details['context']}")

    if details["scope"]:
        body_parts.append(f"## Scope\n\n{details['scope']}")

    if details["non_goals"]:
        body_parts.append(f"## Non-goals\n\n{details['non_goals']}")

    if details["acceptance_criteria"]:
        body_parts.append(
            f"## Acceptance Criteria\n\n{details['acceptance_criteria']}"
        )

    if details["required_tests"]:
        body_parts.append(f"## Required Tests\n\n{details['required_tests']}")

    if details["definition_of_done"]:
        body_parts.append(
            f"## Definition of Done\n\n{details['definition_of_done']}"
        )

    if details["dependencies"]:
        body_parts.append(f"## Dependencies\n\n{details['dependencies']}")

    return "\n\n".join(body_parts)


def create_github_issue(
    title: str,
    body: str,
    dry_run: bool = False,
    labels: Optional[list] = None,
    issue_number: Optional[str] = None,
) -> bool:
    """Create a GitHub issue using gh CLI."""
    if issue_number and not title.startswith(f"TOMATO-{issue_number}:"):
        title = f"TOMATO-{issue_number}: {title}"

    if dry_run:
        print(f"\n{Colors.CYAN}[DRY RUN] Would create issue:{Colors.END}")
        print(f"  {Colors.BOLD}Title:{Colors.END} {title}")
        print(f"  {Colors.BOLD}Body length:{Colors.END} {len(body)} chars")
        if labels:
            print(f"  {Colors.BOLD}Labels:{Colors.END} {', '.join(labels)}")
        return True

    try:
        cmd = ["gh", "issue", "create", "--title", title, "--body", body]

        # Skip labels - they may not exist in the repository yet
        # Labels can be added manually after creation or via separate script

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"{Colors.GREEN}✓ Created: {title}{Colors.END}")
        print(f"  {Colors.BLUE}{result.stdout.strip()}{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}✗ Failed to create: {title}{Colors.END}")
        print(f"  Error: {e.stderr}")
        return False


def check_gh_cli() -> bool:
    """Check if gh CLI is installed and authenticated."""
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print(f"{Colors.RED}Error: GitHub CLI (gh) not found.{Colors.END}")
        print("Install from: https://cli.github.com/")
        return False


def main() -> int:
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv

    # Check prerequisites
    if not check_gh_cli():
        sys.exit(1)

    print(f"{Colors.HEADER}{Colors.BOLD}Stage 1 GitHub Issues Creator{Colors.END}\n")
    print("Reading issues from MVP_GITHUB_ISSUES_COMPLETE.md...")

    # Read and parse issues
    content = read_issues_file()
    raw_issues = extract_issues(content)

    if not raw_issues:
        print(f"{Colors.RED}Error: No issues found in file{Colors.END}")
        sys.exit(1)

    print(f"Found {len(raw_issues)} issues\n")

    # Parse and create issues
    issues_data = [parse_issue_details(issue) for issue in raw_issues]

    if dry_run:
        print(f"{Colors.YELLOW}[DRY RUN MODE]{Colors.END} Issues will NOT be created.\n")
    else:
        print(f"{Colors.YELLOW}Creating {len(issues_data)} issues on GitHub...{Colors.END}\n")

    successful = 0
    failed = 0

    for idx, details in enumerate(issues_data, 1):
        issue_num = details["issue_number"]
        title = details["title"]
        body = format_issue_body(details)

        print(f"[{idx}/{len(issues_data)}] Processing Issue {issue_num}...")

        if create_github_issue(
            title, body, dry_run=dry_run, labels=None, issue_number=issue_num
        ):
            successful += 1
        else:
            failed += 1

    # Summary
    print(f"\n{Colors.BOLD}Summary:{Colors.END}")
    print(f"  {Colors.GREEN}Successful: {successful}{Colors.END}")
    if failed > 0:
        print(f"  {Colors.RED}Failed: {failed}{Colors.END}")

    if dry_run:
        print()
        print(f"{Colors.CYAN}Dry run complete. Run without --dry-run to create issues.{Colors.END}")
    else:
        print()
        print(f"{Colors.GREEN}All issues created!{Colors.END}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
