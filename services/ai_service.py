import os
import json
from pathlib import Path
from openai import OpenAI

from config.ai_guardrails import FORBIDDEN_KEYWORDS
from config.ai_prompts import PORTFOLIO_CONTEXT

client = OpenAI()


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


class AIService:

    def _is_forbidden(self, message: str) -> bool:
        lowered = message.lower()
        return any(keyword in lowered for keyword in FORBIDDEN_KEYWORDS)

    async def process_message(self, message: str) -> str:
        if self._is_forbidden(message):
            return (
                "I can only answer questions related to my "
                "education, work experience, and technical skills."
            )

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
                max_output_tokens=300,
                metadata={
                    "service": "portfolio-api",
                    "env": os.getenv("APP_ENV", "local"),
                    "purpose": "chat",
                },
            )

            return response.output_text

        except Exception as e:
            print("OpenAI error:", e)
            return "Sorry, something went wrong while generating a response."