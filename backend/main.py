import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import (
    auth,
    assessments,
    chat,
    journal,
    moods,
    recommendations,
    documents,
    insights,
    admin,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="MindGuard AI API",
    description="AI-Powered Mental Health Intelligence Platform Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) if settings.ai_provider == "ollama" else "Internal server error"},
    )


app.include_router(auth.router)
app.include_router(assessments.router)
app.include_router(chat.router)
app.include_router(journal.router)
app.include_router(moods.router)
app.include_router(recommendations.router)
app.include_router(documents.router)
app.include_router(insights.router)
app.include_router(admin.router)


@app.get("/api/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "version": "1.0.0",
        "ai_provider": settings.ai_provider,
    }


@app.get("/")
async def root() -> dict:
    return {
        "name": "MindGuard AI API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
