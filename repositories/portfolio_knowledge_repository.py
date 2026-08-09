"""Persistence helpers for the AI assistant's generated portfolio context."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_knowledge(db: AsyncSession) -> dict[str, Any] | None:
    result = await db.execute(
        text("SELECT content FROM portfolio_schema.knowledge_documents WHERE id = 1")
    )
    return result.scalar_one_or_none()


async def get_current_source_hash(db: AsyncSession) -> str | None:
    result = await db.execute(
        text("SELECT source_hash FROM portfolio_schema.knowledge_documents WHERE id = 1")
    )
    return result.scalar_one_or_none()


async def save_knowledge(
    db: AsyncSession,
    *,
    content: dict[str, Any],
    source_site_url: str,
    source_resume_url: str | None,
    source_hash: str,
) -> None:
    await db.execute(
        text(
            """
            INSERT INTO portfolio_schema.knowledge_documents
              (id, content, source_site_url, source_resume_url, source_hash, generated_at, updated_at)
            VALUES
              (1, CAST(:content AS jsonb), :source_site_url, :source_resume_url, :source_hash, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
              content = EXCLUDED.content,
              source_site_url = EXCLUDED.source_site_url,
              source_resume_url = EXCLUDED.source_resume_url,
              source_hash = EXCLUDED.source_hash,
              generated_at = NOW(),
              updated_at = NOW()
            """
        ),
        {
            "content": json.dumps(content),
            "source_site_url": source_site_url,
            "source_resume_url": source_resume_url,
            "source_hash": source_hash,
        },
    )
    await db.commit()
