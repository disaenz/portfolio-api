"""AWS Lambda handler for the scheduled portfolio-knowledge refresh worker."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from scripts.refresh_portfolio_knowledge import refresh

logger = logging.getLogger(__name__)


def handler(event: dict[str, Any], context: Any) -> dict[str, str]:
    """Refresh from EventBridge Scheduler using the API image's worker command."""
    logger.info("Starting scheduled portfolio knowledge refresh: %s", event)
    result = asyncio.run(refresh(write_local_reference=False))
    logger.info("Scheduled portfolio knowledge refresh result: %s", result)
    return result
