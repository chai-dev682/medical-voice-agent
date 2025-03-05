from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger import logger
from app.routers.main import router as twilio_router

app = FastAPI(
    title="Medical Voice Agent",
    description="AI-powered voice agent for medical practice",
    version="0.1.0"
)

app.include_router(twilio_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "AI-powered voice agent for medical practice"}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on 5000 port")
    uvicorn.run(
        "manage:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
