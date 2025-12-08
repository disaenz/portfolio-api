# services/ai_service.py
import os
import json
import re
from pathlib import Path

from langdetect import detect, LangDetectException
from openai import OpenAI

from config.ai_guardrails import FORBIDDEN_KEYWORDS
from config.ai_prompts import PORTFOLIO_CONTEXT

client = OpenAI()


# ---------------------------------------------------------
# Load portfolio knowledge from JSON
# ---------------------------------------------------------


def _load_portfolio_knowledge() -> dict:
    data_path = (
        Path(__file__)
        .resolve()
        .parent
        .parent
        / "data"
        / "portfolio_knowledge.json"
    )

    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


PORTFOLIO_KNOWLEDGE = _load_portfolio_knowledge()


# ---------------------------------------------------------
# Spanish / English fallback messages
# ---------------------------------------------------------

FORBIDDEN_RESPONSE = {
    "en": (
        "I can only answer questions related to my education, "
        "work experience, and technical skills."
    ),
    "es": (
        "Solo puedo responder preguntas relacionadas con mi educación, "
        "experiencia laboral y habilidades técnicas."
    ),
}


# ---------------------------------------------------------
# AI Service
# ---------------------------------------------------------


class AIService:
    def _detect_language(self, text: str) -> str:
        """Attempts to determine if input is Spanish or English."""
        try:
            lang = detect(text)
            return "es" if lang == "es" else "en"
        except LangDetectException:
            return "en"

    def _is_forbidden(self, message: str) -> bool:
        """
        Check if the message hits any forbidden topic.

        Uses word-boundary regex so we don't accidentally match
        substrings like 'languAGEs' for the keyword 'age'.
        """
        lowered = message.lower()

        for keyword in FORBIDDEN_KEYWORDS:
            # Build a safe word-boundary regex for the keyword
            pattern = rf"\b{re.escape(keyword.lower())}\b"
            if re.search(pattern, lowered):
                return True

        return False

    async def process_message(self, message: str) -> str:
        lang = self._detect_language(message)

        if self._is_forbidden(message):
            return FORBIDDEN_RESPONSE[lang]

        # System context + knowledge data
        system_content = (
            PORTFOLIO_CONTEXT
            + "\n\nHere is my portfolio data:\n"
            + json.dumps(PORTFOLIO_KNOWLEDGE, indent=2)
        )

        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": message},
                ],
                max_output_tokens=800,
                metadata={
                    "service": "portfolio-api",
                    "env": os.getenv("APP_ENV", "local"),
                    "purpose": "chat",
                    "lang": lang,
                },
            )

            reply_text = response.output_text or ""

            # If the user spoke Spanish but reply looks non-Spanish,
            # attempt a lightweight translation.
            if lang == "es" and not self._is_spanish(reply_text):
                return await self._translate_to_spanish(reply_text)

            return reply_text

        except Exception as e:
            # Log to stdout so CloudWatch / logs can pick it up
            print("OpenAI error:", e)
            return FORBIDDEN_RESPONSE[lang]

    def _is_spanish(self, text: str) -> bool:
        """Checks if reply is Spanish (very simple heuristic)."""
        lowered = text.lower()
        return any(ch in lowered for ch in "áéíóúñ¿¡")

    async def _translate_to_spanish(self, text: str) -> str:
        """Use OpenAI to translate reply to Spanish when needed."""
        try:
            translation = client.responses.create(
                model="gpt-4o-mini",
                input=(
                    "Translate this to Spanish, keeping a natural first-person voice "
                    "and concise tone:\n\n"
                    f"{text}"
                ),
                max_output_tokens=300,
            )
            return translation.output_text
        except Exception:
            # If translation fails, just return the original English text
            return text