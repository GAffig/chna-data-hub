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

    required_focus_geo_ids = {
        '47059',  # Greene County, TN
        '47163',  # Sullivan County, TN
        '47019',  # Carter County, TN
        '47179',  # Washington County, TN
        '47091',  # Johnson County, TN
        '47067',  # Hancock County, TN
        '47073',  # Hawkins County, TN
        '47171',  # Unicoi County, TN
        '47063',  # Hamblen County, TN
        '47029',  # Cocke County, TN
        '51191',  # Washington County, VA
        '51520',  # Bristol City, VA
        '51167',  # Russell County, VA
        '51173',  # Smyth County, VA
        '51195',  # Wise County, VA
        '51105',  # Lee County, VA
        '51720',  # Norton City, VA
        '51169',  # Scott County, VA
        '51051',  # Dickenson County, VA
        '51077',  # Grayson County, VA
        '51027',  # Buchanan County, VA
        '51185',  # Tazewell County, VA
        '51197',  # Wythe County, VA
    }
    focus_geo_ids = {c['geo_id'] for c in payload['counties'] if c['focus_region']}
    assert required_focus_geo_ids.issubset(focus_geo_ids)


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
