import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import connectors, metrics, runs, sources
from .db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CHNA Data Hub API", version="0.3.0")

raw_origins = os.getenv(
    "APP_CORS_ORIGINS",
    "*",
)
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
allow_any_origin = "*" in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_any_origin else allowed_origins,
    allow_credentials=not allow_any_origin,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(sources.router)
app.include_router(runs.router)
app.include_router(connectors.router)
app.include_router(metrics.router)
