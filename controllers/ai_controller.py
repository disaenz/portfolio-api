from fastapi import APIRouter, HTTPException
from schemas.error import APIError
from models.ai import ChatRequest, ChatResponse
from services.ai_service import AIService

router = APIRouter(
    tags=["AI Chat"],
    responses={
        422: {"model": APIError},
        404: {"model": APIError},
    }
)

# Initialize service
ai_service = AIService()


@router.get("/", summary="Service Health Check")
async def health_check():
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse, summary="Ask the AI about Daniel", description="You may ask in either English or Spanish. The AI will respond in whichever language you use.")
async def chat_with_ai(request: ChatRequest):
    ai_response = await ai_service.process_message(request.message)

    if not ai_response:
        raise HTTPException(status_code=500, detail="Unable to generate response")

    return ChatResponse(reply=ai_response)