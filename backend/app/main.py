"""
AI-Powered Repository Understanding & Documentation Tool
Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import repository, analysis, documentation, chat
from app.config import settings

app = FastAPI(
    title="Repository Analyzer API",
    description="AI-powered tool for repository analysis, explanation, and documentation",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(repository.router, prefix="/api/repository", tags=["Repository"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(documentation.router, prefix="/api/documentation", tags=["Documentation"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.get("/")
async def root():
    return {
        "message": "AI-Powered Repository Understanding & Documentation Tool",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

