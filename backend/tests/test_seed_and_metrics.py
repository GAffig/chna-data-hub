from fastapi.testclient import TestClient

from app.main import app
from app.seed_data import CHNA_REFERENCE_SOURCES


client = TestClient(app)


def test_seed_sources_endpoint_counts() -> None:
    response = client.post('/sources/seed')
    assert response.status_code == 200
    payload = response.json()
    assert payload['inserted'] + payload['skipped'] == len(CHNA_REFERENCE_SOURCES)


def test_metrics_endpoint_ok() -> None:
    response = client.get('/metrics')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_cdc_places_endpoint_validation() -> None:
    response = client.post('/connectors/cdc-places/pull', json={'year': 2025, 'state_abbr': 'TN'})
    # Network call may fail in test env without internet; this confirms route wiring/validation.
    assert response.status_code in (200, 502)
