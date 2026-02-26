from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import SourceAttributionRead
from app.services.internet_research import ResearchIntent, ResearchResult, ResearchRow, parse_intent


client = TestClient(app)


def test_parse_intent_income_ne_tn_2022() -> None:
    intent = parse_intent("The latest income per capital data in NE TN for year 2022")
    assert intent.metric_key in {"per_capita_income", "median_household_income"}
    assert intent.year == 2022
    assert "47" in intent.states
    assert any(geo.startswith("47") for geo in intent.counties)


def test_parse_intent_sw_va_latest() -> None:
    intent = parse_intent("latest diabetes in SW VA")
    assert intent.metric_key == "diabetes_prevalence"
    assert intent.is_latest is True
    assert "51" in intent.states
    assert any(geo.startswith("51") for geo in intent.counties)


def test_research_search_endpoint_mocked(monkeypatch) -> None:
    def fake_run_internet_research(query: str, limit: int = 200) -> ResearchResult:
        return ResearchResult(
            query=query,
            intent=ResearchIntent(
                metric_key="per_capita_income",
                metric_name="Per Capita Income",
                domain="Income and Economics",
                year=2024,
                is_latest=True,
                states=["47"],
                counties=["47059"],
                geography_scope="Focus region counties (NE TN + SW VA)",
                source_priority=["US Census ACS"],
            ),
            items=[
                ResearchRow(
                    metric_key="per_capita_income",
                    metric_name="Per Capita Income",
                    year=2024,
                    geo_id="47059",
                    geo_name="Greene County, Tennessee",
                    value=30123.0,
                    unit="USD",
                    source_name="US Census ACS",
                    source_url="https://api.census.gov",
                    retrieved_at=datetime.now(UTC),
                )
            ],
            sources=[
                SourceAttributionRead(
                    name="US Census ACS",
                    url="https://www.census.gov/data/developers/data-sets/acs-5year.html",
                    citation="U.S. Census Bureau",
                    category="Federal Data",
                )
            ],
            note="Live internet retrieval from prioritized CHNA references.",
        )

    monkeypatch.setattr("app.api.research.run_internet_research", fake_run_internet_research)
    response = client.get("/research/search?q=latest per capita income in NE TN")
    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "latest per capita income in NE TN"
    assert payload["total_results"] == 1
    assert payload["intent"]["metric_key"] == "per_capita_income"
