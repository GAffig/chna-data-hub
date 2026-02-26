from fastapi import APIRouter, HTTPException, Query

from ..schemas import ResearchIntentRead, ResearchResultRead, ResearchSearchResponse
from ..services.internet_research import run_internet_research

router = APIRouter(prefix="/research", tags=["research"])


@router.get("/search", response_model=ResearchSearchResponse)
def research_search(
    q: str = Query(min_length=2),
    limit: int = Query(default=250, ge=1, le=5000),
):
    try:
        result = run_internet_research(query=q, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Internet research failed: {exc}") from exc

    return ResearchSearchResponse(
        query=result.query,
        intent=ResearchIntentRead(**result.intent.__dict__),
        total_results=len(result.items),
        items=[ResearchResultRead(**item.__dict__) for item in result.items],
        sources=result.sources,
        note=result.note,
    )
