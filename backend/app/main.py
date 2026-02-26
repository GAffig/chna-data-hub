from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import connectors, metrics, runs, sources
from .db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CHNA Data Hub API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
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
