import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.scraper import router as scraper_router
from app.routes.reviews import router as reviews_router
from app.routes.schedule import router as schedule_router
from app.services.scheduler_service import start_scheduler, stop_scheduler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

app = FastAPI(
    title="Google Play Scraper API",
    description="API para scraping de reviews e dados de apps da Google Play Store.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — permite uso com frontends locais ou externos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(scraper_router)
app.include_router(reviews_router)
app.include_router(schedule_router)


@app.on_event("startup")
async def startup_event():
    """Inicia o scheduler ao subir a aplicação."""
    start_scheduler()


@app.on_event("shutdown")
def shutdown_event():
    """Para o scheduler ao desligar a aplicação."""
    stop_scheduler()


@app.get("/health", tags=["Status"])
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=True,
    )
