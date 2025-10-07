"""Utility functions for file handling and naming conventions."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional


def ensure_dir(path: str | Path) -> None:
    """Ensure that a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure existence for.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def write_text_file(path: str | Path, content: str, encoding: str = "utf-8") -> None:
    """Write text content to a file atomically.

    The file is first written to a temporary file and then renamed to the target path
    to reduce the risk of partial writes.

    Args:
        path: File path to write to.
        content: Text content to write.
        encoding: File encoding (default 'utf-8').
    """
    path = Path(path)
    ensure_dir(path.parent)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding=encoding) as f:
        f.write(content)
    tmp_path.replace(path)


def iso_date_string(d: Optional[date] = None) -> str:
    """Return an ISO date string in YYYYMMDD format.

    Args:
        d: Date object to format. Defaults to today.

    Returns:
        A string representing the date in YYYYMMDD format.
    """
    d = d or date.today()
    return d.strftime("%Y%m%d")


def branch_name_for_date(d: Optional[date] = None) -> str:
    """Return a feature branch name for a given date.

    Example: 'feature/news-20251007'

    Args:
        d: Optional date. Defaults to today.

    Returns:
        Branch name string.
    """
    return f"feature/news-{iso_date_string(d)}"


def digest_filename_for_date(d: Optional[date] = None) -> str:
    """Return the digest filename for a given date.

    Example: 'digest_20251007.md'

    Args:
        d: Optional date. Defaults to today.

    Returns:
        Digest filename string.
    """
    return f"digest_{iso_date_string(d)}.md"


def write_branch_name_file(repo_root: str | Path, branch_name: str) -> None:
    """Persist the branch name into `repo_root/branch_name.txt`.

    This file is read by the workflow to create the PR using GitHub CLI.

    Args:
        repo_root: Root directory of the repository.
        branch_name: Branch name to write.
    """
    path = Path(repo_root) / "branch_name.txt"
    write_text_file(path, branch_name)
