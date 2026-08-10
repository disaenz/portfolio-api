"""AWS Lambda handler for the scheduled portfolio-knowledge refresh worker."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from scripts.refresh_portfolio_knowledge import refresh

logger = logging.getLogger(__name__)


def _notify_refresh_failure(error: Exception, context: Any) -> None:
    """Send an SES alert without masking the original scheduled-job failure."""
    request_id = getattr(context, "aws_request_id", "unknown")
    subject = "Portfolio knowledge refresh failed"
    body = (
        "The scheduled portfolio knowledge refresh did not complete.\n\n"
        f"Request ID: {request_id}\n"
        f"Error type: {type(error).__name__}\n"
        f"Error: {error}\n\n"
        "Check the CloudWatch logs for the portfolio-knowledge-refresh Lambda."
    )

    try:
        # Import lazily so a notification configuration problem never prevents
        # a normal refresh from running.
        from services.email_service import send_email

        result = send_email(subject, body)
        if result.get("status") != "success":
            logger.error("Refresh failure email was not sent: %s", result.get("error"))
    except Exception:
        logger.exception("Unable to send portfolio refresh failure email")


def handler(event: dict[str, Any], context: Any) -> dict[str, str]:
    """Refresh from EventBridge Scheduler using the API image's worker command."""
    logger.info("Starting scheduled portfolio knowledge refresh: %s", event)
    try:
        result = asyncio.run(refresh(write_local_reference=False))
        logger.info("Scheduled portfolio knowledge refresh result: %s", result)
        return result
    except Exception as error:
        logger.exception("Scheduled portfolio knowledge refresh failed")
        _notify_refresh_failure(error, context)
        raise
