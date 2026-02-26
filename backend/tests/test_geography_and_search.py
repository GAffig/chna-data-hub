from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_geography_options_focus_region_present() -> None:
    response = client.get('/geography/options')
    assert response.status_code == 200
    payload = response.json()

    states = {s['abbr'] for s in payload['states']}
    assert 'TN' in states
    assert 'VA' in states
    assert any(c['focus_region'] for c in payload['counties'])


def test_metrics_facets_ok() -> None:
    response = client.get('/metrics/facets')
    assert response.status_code == 200
    payload = response.json()
    assert 'years' in payload
    assert 'sources' in payload
    assert 'measures' in payload


def test_metrics_export_csv_ok() -> None:
    response = client.get('/metrics/export/csv?limit=10')
    assert response.status_code == 200
    assert response.headers.get('content-type', '').startswith('text/csv')
    assert 'source_name,measure_code,measure_name' in response.text


def test_search_endpoint_ok() -> None:
    response = client.get('/search?q=diabetes')
    assert response.status_code == 200
    payload = response.json()
    assert payload['query'] == 'diabetes'
    assert isinstance(payload['items'], list)
    assert isinstance(payload['sources'], list)


def test_search_query_validation() -> None:
    response = client.get('/search?q=d')
    assert response.status_code == 422
