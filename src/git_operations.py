"""Git operations using GitPython, isolated for easier testing."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from git import Repo, GitCommandError, InvalidGitRepositoryError


class GitManager:
    """Manages Git operations for a repository at `config.fork_path`.

    Allows optional injection of `Repo` for testing/mocking.
    """

    def __init__(self, config, logger, repo: Optional[Repo] = None) -> None:
        self.config = config
        self.logger = logger

        if repo:
            self.repo = repo
        else:
            try:
                self.repo = Repo(self.config.fork_path)
            except InvalidGitRepositoryError as exc:
                logger.exception("Invalid Git repository at %s", self.config.fork_path)
                raise

    def _get_remote(self, name: str) -> Optional[Repo.remote]:
        """Return the remote object with the given name, or None if not found."""
        return next((r for r in self.repo.remotes if r.name == name), None)

    def _checkout_or_create_branch(self, name: str) -> None:
        """Checkout an existing branch or create it based on HEAD if missing."""
        if name in self.repo.heads:
            self.repo.heads[name].checkout()
            self.logger.debug("Checked out existing branch %s", name)
        else:
            self.repo.create_head(name).checkout()
            self.logger.debug("Created and checked out new branch %s", name)

    def sync_with_upstream(self) -> None:
        """Fetch and merge `upstream/main` into local main (best-effort)."""
        try:
            upstream = self._get_remote(self.config.remote_upstream)
            if upstream is None:
                upstream = self.repo.create_remote(
                    self.config.remote_upstream, self.config.repo_url_alt
                )
                self.logger.info(
                    "Added upstream remote %s -> %s",
                    self.config.remote_upstream,
                    self.config.repo_url_alt,
                )

            # Fetch upstream
            upstream.fetch()

            main_branch = "main"

            if main_branch in self.repo.heads:
                self.repo.git.checkout(main_branch)
            elif f"{self.config.remote_upstream}/{main_branch}" in self.repo.refs:
                self.repo.git.checkout(
                    "-b",
                    main_branch,
                    f"{self.config.remote_upstream}/{main_branch}",
                )
            else:
                self.repo.create_head(main_branch).checkout()
                self.logger.warning(
                    "Created 'main' from current HEAD; upstream 'main' not found."
                )

            self.repo.git.pull(self.config.remote_upstream, main_branch)
            self.logger.info("Synchronized fork with upstream/%s.", main_branch)

        except GitCommandError as exc:
            self.logger.warning("Could not fully sync with upstream: %s", exc)

    def commit_and_push(
        self, branch_name: str, file_path: str, commit_message: Optional[str] = None
    ) -> None:
        """Create branch, add file, commit, and push to origin.

        Args:
            branch_name: Branch to create and push.
            file_path: Absolute path to the file to add.
            commit_message: Optional commit message; auto-generated if None.
        """
        commit_message = commit_message or f"feat: add {os.path.basename(file_path)}"

        try:
            self._checkout_or_create_branch(branch_name)
            relpath = os.path.relpath(file_path, self.repo.working_tree_dir)
            self.repo.index.add([relpath])
            self.repo.index.commit(commit_message)
            origin = self.repo.remote("origin")
            origin.push(branch_name)
            self.logger.info("Pushed branch %s to origin", branch_name)

        except GitCommandError as exc:
            self.logger.exception("Git operation failed: %s", exc)
            raise

    def push_logs_to_branch(self) -> None:
        """Commit logs/ directory and push to a dedicated log branch (best-effort)."""
        try:
            branch_name = self.config.log_branch
            self._checkout_or_create_branch(branch_name)

            logs_dir = os.path.join(os.getcwd(), "logs")
            if not os.path.exists(logs_dir):
                self.logger.info("No logs to push.")
                return

            rel_logs_dir = os.path.relpath(logs_dir, self.repo.working_tree_dir)
            self.repo.index.add([rel_logs_dir])
            self.repo.index.commit(
                f"chore: update logs {datetime.utcnow().isoformat()}"
            )

            origin = self.repo.remote("origin")
            origin.push(branch_name)
            self.logger.info("Logs pushed to branch %s", branch_name)

        except Exception as exc:
            self.logger.warning("Could not push logs branch: %s", exc)
