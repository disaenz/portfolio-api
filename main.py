from fastapi import FastAPI
from controllers.grant_controller import router as grant_router
import logging
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Portfolio API",
    version="v1.1.1",
    description=(
        "A scalable backend API powering the Daniel Saenz ecosystem. "
        "Currently supports grant management features and is designed to "
        "expand with new capabilities—including future AI-driven functionality "
        "to enhance portfolio interactivity and automation."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Daniel Saenz",
        "email": "disaenz2@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

origins = [
    "http://localhost:3000",
    "http://localhost:8081",
    "https://daniel-saenz.com",
    "https://www.daniel-saenz.com",
    "https://grants.daniel-saenz.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active APIs
app.include_router(grant_router, prefix="/api/grants")

# Future AI / Chatbot endpoint (placeholder for expansion)
# app.include_router(ai_router, prefix="/ai", tags=["AI Assistant"])

# AWS Lambda Handler
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)