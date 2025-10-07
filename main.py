"""Orchestrator entrypoint for the daily contributor bot."""

from __future__ import annotations

import sys

from src.config import Config
from src.logger import setup_logger
from src.content_generator import ContentGenerator
from src.git_operations import GitManager


def main() -> None:
    """Run the daily contribution workflow end-to-end."""
    logger = setup_logger()
    config = Config()
    logger.info("Starting daily contributor workflow.")

    try:
        # Initialize GitManager and ContentGenerator
        git_manager = GitManager(config, logger)
        generator = ContentGenerator(config, logger)

        # Sync fork with upstream (best-effort)
        git_manager.sync_with_upstream()

        # Generate daily content and commit/push
        branch_name, file_path = generator.generate_daily_content()
        git_manager.commit_and_push(branch_name, file_path)
        logger.info("Content branch created and pushed: %s", branch_name)

        # Optionally push logs to dedicated branch
        if config.enable_log_branch:
            git_manager.push_logs_to_branch()

        logger.info("Workflow finished successfully.")

    except Exception as exc:
        logger.exception("Fatal error during workflow: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
