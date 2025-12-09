import os
import json
from pathlib import Path
from typing import List, Dict, Optional

from langdetect import detect, LangDetectException
from openai import OpenAI

from config.ai_guardrails import is_forbidden_message
from config.ai_prompts import PORTFOLIO_CONTEXT

client = OpenAI()


# ---------------------------------------------------------
# Load portfolio knowledge JSON
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

SAFE_HISTORY_LIMIT = 6


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
        try:
            return "es" if detect(text) == "es" else "en"
        except LangDetectException:
            return "en"

    def _build_conversation(
        self,
        history: Optional[List[Dict[str, str]]],
        latest_user_message: str,
    ) -> List[Dict[str, str]]:
        conversation: List[Dict[str, str]] = []

        if history:
            trimmed = history[-SAFE_HISTORY_LIMIT:]
            for item in trimmed:
                role = "assistant" if item.get("role") == "assistant" else "user"
                content = item.get("content", "")
                if content:
                    conversation.append({"role": role, "content": content})

        conversation.append({"role": "user", "content": latest_user_message})
        return conversation

    async def process_message(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:

        lang = self._detect_language(message)

        # Apply category-based guardrails
        if is_forbidden_message(message):
            return FORBIDDEN_RESPONSE[lang]

        # System + knowledge context
        system_content = (
            PORTFOLIO_CONTEXT
            + "\n\nHere is my portfolio data:\n"
            + json.dumps(PORTFOLIO_KNOWLEDGE, indent=2)
        )

        conversation_messages = self._build_conversation(history, message)

        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {"role": "system", "content": system_content},
                    *conversation_messages,
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

            if lang == "es" and not self._is_spanish(reply_text):
                return await self._translate_to_spanish(reply_text)

            return reply_text

        except Exception as e:
            print("OpenAI error:", e)
            return FORBIDDEN_RESPONSE[lang]

    def _is_spanish(self, text: str) -> bool:
        lowered = text.lower()
        return any(ch in lowered for ch in "áéíóúñ¿¡")

    async def _translate_to_spanish(self, text: str) -> str:
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
            return text