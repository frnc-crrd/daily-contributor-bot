"""Configuration manager: Centralizes the loading of environment variables."""

from __future__ import annotations

import os
from typing import Optional


class Config:
    """Centralized configuration holder for the application.

    Loads and exposes environment variables used across the project.
    All values are fetched once at initialization time.
    """

    def __init__(self) -> None:
        self.repo_owner_alt: Optional[str] = os.getenv("REPO_OWNER_ALT")
        self.repo_name_alt: Optional[str] = os.getenv("REPO_NAME_ALT")
        self.repo_url_alt: Optional[str] = self._build_repo_url()

        self.fork_path: Optional[str] = os.getenv("FORK_PATH")
        self.remote_upstream: Optional[str] = os.getenv("REMOTE_UPSTREAM")
        self.news_dir: Optional[str] = os.getenv("NEWS_DIR")

        self.enable_log_branch: bool = self._get_bool_env("ENABLE_LOG_BRANCH")
        self.log_branch: Optional[str] = os.getenv("LOG_BRANCH")
        self.approved_user: Optional[str] = os.getenv("APPROVED_USER")

    def _build_repo_url(self) -> Optional[str]:
        """Constructs the GitHub repository URL if owner and name are available."""
        if self.repo_owner_alt and self.repo_name_alt:
            return f"https://github.com/{self.repo_owner_alt}/{self.repo_name_alt}.git"
        return None

    @staticmethod
    def _get_bool_env(var_name: str, default: bool = False) -> bool:
        """Converts an environment variable to a boolean value."""
        value = os.getenv(var_name)
        return str(value).strip().lower() == "true" if value is not None else default

    def __repr__(self) -> str:
        """String representation for debugging purposes."""
        return (
            f"{self.__class__.__name__}("
            f"repo_owner_alt={self.repo_owner_alt!r}, "
            f"repo_name_alt={self.repo_name_alt!r}, "
            f"enable_log_branch={self.enable_log_branch!r})"
        )
