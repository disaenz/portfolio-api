from fastapi import FastAPI
from controllers.grant_controller import router as grant_router
from controllers.ai_controller import router as ai_router
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
    version="v1.2.9",
    description=(
        "Backend service powering Daniel's portfolio, including grant management and AI-powered Q&A about his experience."
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
    "http://localhost:5173",
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
app.include_router(ai_router, prefix="/api/ai")


# AWS Lambda Handler
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)