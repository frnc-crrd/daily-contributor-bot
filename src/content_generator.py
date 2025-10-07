"""Encapsulates the generation of daily content in Markdown format."""

from __future__ import annotations

import os
import random
from datetime import date
from typing import Optional, Tuple

from .utils import (
    branch_name_for_date,
    digest_filename_for_date,
    write_text_file,
    ensure_dir,
)


class ContentGenerator:
    """Generates and persists daily Markdown digest files."""

    def __init__(self, config, logger) -> None:
        self.config = config
        self.logger = logger

    def _build_content(self, d: date) -> str:
        """Builds the Markdown content for a given date.

        Args:
            d: The date for which to generate the digest.

        Returns:
            A string containing the Markdown-formatted digest.
        """
        date_str = d.strftime("%A, %B %d, %Y")
        headlines = [
            "Quantum progress: stable qubits announced.",
            "Python 4.0: rumors about stricter typing.",
            "GitHub Copilot improves unit test generation.",
            "Generative AI is reshaping UI/UX design.",
        ]
        chosen_headline = random.choice(headlines)

        return (
            f"# Daily Tech Digest - {date_str}\n\n"
            f"## {chosen_headline}\n\n"
            "This digest explores how automation is reshaping developer "
            "workflows: from CI to automated PR approvals. This repository "
            "demonstrates an automated content pipeline.\n\n"
            "---\n\n"
            "Generated automatically by the daily contributor bot."
        )

    def generate_daily_content(self, d: Optional[date] = None) -> Tuple[str, str]:
        """Generates the digest file and returns the branch name and file path.

        Args:
            d: Optional date to generate the digest for. Defaults to today.

        Returns:
            A tuple of (branch_name, absolute_file_path).
        """
        d = d or date.today()
        branch_name = branch_name_for_date(d)
        filename = digest_filename_for_date(d)

        news_dir = os.path.join(self.config.fork_path, self.config.news_dir)
        ensure_dir(news_dir)
        file_path = os.path.join(news_dir, filename)

        content = self._build_content(d)

        # Write digest file
        try:
            write_text_file(file_path, content)
            self.logger.info("Generated content at %s", file_path)
        except Exception as exc:
            self.logger.exception("Failed to write digest file: %s", exc)
            raise

        # Persist branch name for workflow use
        branch_file_path = os.path.join(self.config.fork_path, "branch_name.txt")
        try:
            write_text_file(branch_file_path, branch_name)
            self.logger.debug("Wrote branch_name.txt with %s", branch_name)
        except Exception as exc:
            self.logger.exception("Could not persist branch_name.txt: %s", exc)

        return branch_name, file_path
