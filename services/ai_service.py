import os
import json

from langdetect import detect, LangDetectException
from openai import OpenAI

from config.ai_guardrails import is_forbidden_message
from config.ai_prompts import (
    PORTFOLIO_CONTEXT,
    FALLBACK_OUT_OF_SCOPE_EN,
    FALLBACK_OUT_OF_SCOPE_ES,
    FALLBACK_MISSING_KNOWLEDGE_EN,
    FALLBACK_MISSING_KNOWLEDGE_ES,
)
from services.email_service import send_email  # <-- EMAIL SERVICE
from database import AsyncSessionLocal
from repositories.portfolio_knowledge_repository import get_current_knowledge

client = OpenAI()
AI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SAFE_HISTORY_LIMIT = 6


class AIService:

    # -----------------------------
    # Language detection
    # -----------------------------
    def _detect_language(self, text: str) -> str:
        try:
            return "es" if detect(text) == "es" else "en"
        except LangDetectException:
            return "en"

    # -----------------------------
    # Build conversation payload
    # -----------------------------
    def _build_conversation(self, history, latest_user_message):
        conversation = []

        if history:
            trimmed = history[-SAFE_HISTORY_LIMIT:]
            for item in trimmed:
                role = "assistant" if item.get("role") == "assistant" else "user"
                content = item.get("content", "")
                if content:
                    conversation.append({"role": role, "content": content})

        conversation.append({"role": "user", "content": latest_user_message})
        return conversation

    # -----------------------------
    async def _get_portfolio_knowledge(self) -> dict | None:
        """Read the current generated context from PostgreSQL for every chat."""
        try:
            async with AsyncSessionLocal() as db:
                return await get_current_knowledge(db)
        except Exception as error:
            print("Portfolio knowledge database error:", error)
            return None

    # Email alert for missing generated knowledge
    # -----------------------------
    def _trigger_missing_knowledge_email(self, user_question, history):
        if history:
            trimmed = history[-5:]
            hist_lines = [
                f"{msg.get('role','user').upper()}: {msg.get('content','')}"
                for msg in trimmed
            ]
            history_text = "\n".join(hist_lines)
        else:
            history_text = "No history available."

        subject = "Portfolio AI Missing Knowledge Alert"

        body = (
            "The AI assistant could not answer the following professional question due "
            "to missing generated portfolio knowledge.\n\n"
            f"User Question:\n{user_question}\n\n"
            "Recent Chat History:\n"
            "--------------------------------------------------\n"
            f"{history_text}\n\n"
            "Action: run scripts/refresh_portfolio_knowledge.py after updating the site or resume."
        )

        send_email(subject, body)

    # -----------------------------
    # MAIN CHAT HANDLER
    # -----------------------------
    async def process_message(self, message: str, history=None) -> str:

        lang = self._detect_language(message)

        # 1. PERSONAL / OFF-LIMIT questions blocked immediately
        if is_forbidden_message(message):
            return FALLBACK_OUT_OF_SCOPE_ES if lang == "es" else FALLBACK_OUT_OF_SCOPE_EN

        # 2. System + database-backed data
        portfolio_knowledge = await self._get_portfolio_knowledge()
        if not portfolio_knowledge:
            return FALLBACK_MISSING_KNOWLEDGE_ES if lang == "es" else FALLBACK_MISSING_KNOWLEDGE_EN

        system_content = (
            PORTFOLIO_CONTEXT
            + "\n\nHere is my portfolio data:\n"
            + json.dumps(portfolio_knowledge, indent=2)
        )

        conversation_messages = self._build_conversation(history, message)

        try:
            response = client.responses.create(
                model=AI_MODEL,
                input=[{"role": "system", "content": system_content}, *conversation_messages],
                max_output_tokens=800,
                metadata={
                    "service": "portfolio-api",
                    "env": os.getenv("APP_ENV", "local"),
                    "purpose": "chat",
                    "lang": lang,
                },
            )

            reply_text = response.output_text or ""

            # -----------------------------
            # Detect MISSING KNOWLEDGE fallback
            # (only email for professional questions missing JSON data)
            # -----------------------------
            missing_fallback = (
                FALLBACK_MISSING_KNOWLEDGE_ES if lang == "es" else FALLBACK_MISSING_KNOWLEDGE_EN
            )

            if reply_text.strip() == missing_fallback.strip():
                self._trigger_missing_knowledge_email(message, history)

            # -----------------------------
            # Detect OUT-OF-SCOPE (personal) fallback
            # (NO EMAIL should be sent)
            # -----------------------------
            out_of_scope_fallback = (
                FALLBACK_OUT_OF_SCOPE_ES if lang == "es" else FALLBACK_OUT_OF_SCOPE_EN
            )

            if reply_text.strip() == out_of_scope_fallback.strip():
                return reply_text  # return immediately, NO email

            # -----------------------------
            # Auto-translate to Spanish if needed
            # -----------------------------
            if lang == "es" and not self._is_spanish(reply_text):
                return await self._translate_to_spanish(reply_text)

            return reply_text

        except Exception as e:
            print("OpenAI error:", e)
            return FALLBACK_OUT_OF_SCOPE_ES if lang == "es" else FALLBACK_OUT_OF_SCOPE_EN

    # -----------------------------
    # Spanish detection helper
    # -----------------------------
    def _is_spanish(self, text: str) -> bool:
        lowered = text.lower()
        return any(c in lowered for c in "áéíóúñ¿¡")

    # -----------------------------
    # Translation helper
    # -----------------------------
    async def _translate_to_spanish(self, text: str) -> str:
        try:
            translation = client.responses.create(
                model=AI_MODEL,
                input=f"Translate this to Spanish while preserving tone:\n{text}",
                max_output_tokens=200,
            )
            return translation.output_text
        except Exception:
            return text
