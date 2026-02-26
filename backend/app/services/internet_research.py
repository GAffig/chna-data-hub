import re
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from ..schemas import SourceAttributionRead
from ..seed_data import CHNA_REFERENCE_SOURCES


@dataclass
class ResearchIntent:
    metric_key: str
    metric_name: str
    domain: str
    year: int | None
    is_latest: bool
    states: list[str]
    counties: list[str]
    geography_scope: str
    source_priority: list[str]


@dataclass
class ResearchRow:
    metric_key: str
    metric_name: str
    year: int
    geo_id: str
    geo_name: str
    value: float
    unit: str
    source_name: str
    source_url: str
    retrieved_at: datetime


@dataclass
class ResearchResult:
    query: str
    intent: ResearchIntent
    items: list[ResearchRow]
    sources: list[SourceAttributionRead]
    note: str


FOCUS_COUNTIES = [
    {"geo_id": "47059", "name": "Greene County", "state_fips": "47"},
    {"geo_id": "47163", "name": "Sullivan County", "state_fips": "47"},
    {"geo_id": "47019", "name": "Carter County", "state_fips": "47"},
    {"geo_id": "47179", "name": "Washington County", "state_fips": "47"},
    {"geo_id": "47091", "name": "Johnson County", "state_fips": "47"},
    {"geo_id": "47067", "name": "Hancock County", "state_fips": "47"},
    {"geo_id": "47073", "name": "Hawkins County", "state_fips": "47"},
    {"geo_id": "47171", "name": "Unicoi County", "state_fips": "47"},
    {"geo_id": "47063", "name": "Hamblen County", "state_fips": "47"},
    {"geo_id": "47029", "name": "Cocke County", "state_fips": "47"},
    {"geo_id": "51191", "name": "Washington County", "state_fips": "51"},
    {"geo_id": "51520", "name": "Bristol City", "state_fips": "51"},
    {"geo_id": "51167", "name": "Russell County", "state_fips": "51"},
    {"geo_id": "51173", "name": "Smyth County", "state_fips": "51"},
    {"geo_id": "51195", "name": "Wise County", "state_fips": "51"},
    {"geo_id": "51105", "name": "Lee County", "state_fips": "51"},
    {"geo_id": "51720", "name": "Norton City", "state_fips": "51"},
    {"geo_id": "51169", "name": "Scott County", "state_fips": "51"},
    {"geo_id": "51051", "name": "Dickenson County", "state_fips": "51"},
    {"geo_id": "51077", "name": "Grayson County", "state_fips": "51"},
    {"geo_id": "51027", "name": "Buchanan County", "state_fips": "51"},
    {"geo_id": "51185", "name": "Tazewell County", "state_fips": "51"},
    {"geo_id": "51197", "name": "Wythe County", "state_fips": "51"},
]


STATE_FIPS_TO_ABBR = {"47": "TN", "51": "VA"}


METRICS = [
    {
        "key": "per_capita_income",
        "name": "Per Capita Income (past 12 months, inflation-adjusted)",
        "domain": "Income and Economics",
        "source": "census_acs",
        "census_variable": "B19301_001E",
        "unit": "USD",
        "keywords": ["per capita income", "income per capita", "income"],
    },
    {
        "key": "median_household_income",
        "name": "Median Household Income (past 12 months, inflation-adjusted)",
        "domain": "Income and Economics",
        "source": "census_acs",
        "census_variable": "B19013_001E",
        "unit": "USD",
        "keywords": ["median household income", "household income", "median income"],
    },
    {
        "key": "population",
        "name": "Total Population",
        "domain": "Demographics",
        "source": "census_acs",
        "census_variable": "B01003_001E",
        "unit": "people",
        "keywords": ["population", "total population", "pop"],
    },
    {
        "key": "diabetes_prevalence",
        "name": "Diagnosed Diabetes Prevalence",
        "domain": "Chronic Disease",
        "source": "cdc_places",
        "places_terms": ["diagnosed diabetes"],
        "unit": "percent",
        "keywords": ["diabetes"],
    },
    {
        "key": "obesity_prevalence",
        "name": "Obesity Prevalence",
        "domain": "Health Behaviors",
        "source": "cdc_places",
        "places_terms": ["obesity among adults"],
        "unit": "percent",
        "keywords": ["obesity", "overweight"],
    },
]

LATEST_TERMS = {"latest", "most recent", "current", "newest"}
NE_TN_TERMS = {"ne tn", "northeast tn", "northeast tennessee"}
SW_VA_TERMS = {"sw va", "southwest va", "southwest virginia"}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _focus_ids_for_state(state_fips: str) -> list[str]:
    return [row["geo_id"] for row in FOCUS_COUNTIES if row["state_fips"] == state_fips]


def _detect_metric(query: str) -> dict:
    normalized = _normalize(query)
    for metric in METRICS:
        if any(keyword in normalized for keyword in metric["keywords"]):
            return metric
    return METRICS[0]


def parse_intent(query: str) -> ResearchIntent:
    normalized = _normalize(query)
    metric = _detect_metric(normalized)

    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", normalized)
    year = int(year_match.group(1)) if year_match else None
    is_latest = any(term in normalized for term in LATEST_TERMS) or year is None

    states: set[str] = set()
    counties: set[str] = set()
    explicit_state = False

    if any(term in normalized for term in NE_TN_TERMS):
        states.add("47")
        counties.update(_focus_ids_for_state("47"))
    if any(term in normalized for term in SW_VA_TERMS):
        states.add("51")
        counties.update(_focus_ids_for_state("51"))

    if "tennessee" in normalized or re.search(r"\btn\b", normalized):
        states.add("47")
        explicit_state = True
    if "virginia" in normalized or re.search(r"\bva\b", normalized):
        states.add("51")
        explicit_state = True

    for county in FOCUS_COUNTIES:
        county_name = _normalize(county["name"])
        short_name = county_name.replace(" county", "").replace(" city", "")
        if county_name in normalized or short_name in normalized:
            counties.add(county["geo_id"])
            states.add(county["state_fips"])

    if not states:
        states.update({"47", "51"})
    if not counties and not explicit_state:
        counties.update(_focus_ids_for_state("47"))
        counties.update(_focus_ids_for_state("51"))

    if counties and len(counties) == len(_focus_ids_for_state("47")) + len(_focus_ids_for_state("51")):
        geography_scope = "Focus region counties (NE TN + SW VA)"
    elif counties:
        geography_scope = f"{len(counties)} selected county/city areas"
    else:
        geography_scope = f"All counties in states: {', '.join(sorted(states))}"

    source_priority = ["US Census ACS", "CDC PLACES", "Other CHNA references"]
    return ResearchIntent(
        metric_key=metric["key"],
        metric_name=metric["name"],
        domain=metric["domain"],
        year=year,
        is_latest=is_latest,
        states=sorted(states),
        counties=sorted(counties),
        geography_scope=geography_scope,
        source_priority=source_priority,
    )


def _source_lookup() -> dict[str, SourceAttributionRead]:
    mapped = {}
    for row in CHNA_REFERENCE_SOURCES:
        mapped[row["name"]] = SourceAttributionRead(
            name=row["name"],
            url=row["url"],
            citation=row["citation"],
            category=row["category"],
        )
    return mapped


def _candidate_years(intent: ResearchIntent, minimum_year: int) -> list[int]:
    if intent.year is not None:
        return [intent.year]
    current_year = datetime.now(UTC).year
    return list(range(current_year - 1, minimum_year - 1, -1))


def _fetch_census_rows(intent: ResearchIntent, metric: dict, limit: int) -> list[ResearchRow]:
    years = _candidate_years(intent, 2010)
    variable = metric["census_variable"]
    rows: list[ResearchRow] = []

    for year in years:
        rows.clear()
        for state in intent.states:
            url = f"https://api.census.gov/data/{year}/acs/acs5"
            params = {"get": f"NAME,{variable}", "for": "county:*", "in": f"state:{state}"}
            response = httpx.get(url, params=params, timeout=40.0)
            if response.status_code != 200:
                rows.clear()
                break
            data = response.json()
            if not isinstance(data, list) or len(data) <= 1:
                rows.clear()
                break

            header = data[0]
            idx_name = header.index("NAME")
            idx_value = header.index(variable)
            idx_state = header.index("state")
            idx_county = header.index("county")

            for raw in data[1:]:
                value_str = raw[idx_value]
                if value_str in ("", "null", None, "-666666666"):
                    continue
                try:
                    value = float(value_str)
                except ValueError:
                    continue
                geo_id = f"{raw[idx_state]}{raw[idx_county]}"
                if intent.counties and geo_id not in intent.counties:
                    continue
                rows.append(
                    ResearchRow(
                        metric_key=metric["key"],
                        metric_name=metric["name"],
                        year=year,
                        geo_id=geo_id,
                        geo_name=raw[idx_name],
                        value=value,
                        unit=metric["unit"],
                        source_name="US Census ACS",
                        source_url=f"{url}?get=NAME,{variable}&for=county:*&in=state:{state}",
                        retrieved_at=datetime.now(UTC),
                    )
                )
        if rows:
            rows.sort(key=lambda row: (row.year, row.geo_name))
            return rows[:limit]
    return []


def _fetch_places_rows(intent: ResearchIntent, metric: dict, limit: int) -> list[ResearchRow]:
    years = _candidate_years(intent, 2020)
    places_terms = [term.lower() for term in metric["places_terms"]]
    rows: list[ResearchRow] = []

    for year in years:
        rows.clear()
        for state_fips in intent.states:
            state_abbr = STATE_FIPS_TO_ABBR.get(state_fips)
            if not state_abbr:
                continue
            url = "https://data.cdc.gov/resource/swc5-untb.json"
            params = {
                "$select": "locationid,locationname,measureid,measure,data_value,data_value_unit,year,stateabbr",
                "$where": f"stateabbr='{state_abbr}' AND year='{year}' AND data_value IS NOT NULL",
                "$limit": 50000,
            }
            response = httpx.get(url, params=params, timeout=40.0)
            if response.status_code != 200:
                rows.clear()
                break
            data = response.json()
            if not isinstance(data, list):
                rows.clear()
                break

            for raw in data:
                measure_name = _normalize(str(raw.get("measure", "")))
                if not any(term in measure_name for term in places_terms):
                    continue
                geo_id = str(raw.get("locationid", ""))
                if len(geo_id) != 5:
                    continue
                if intent.counties and geo_id not in intent.counties:
                    continue
                value_str = raw.get("data_value")
                try:
                    value = float(value_str)
                except (TypeError, ValueError):
                    continue
                rows.append(
                    ResearchRow(
                        metric_key=metric["key"],
                        metric_name=str(raw.get("measure", metric["name"])),
                        year=int(raw.get("year", year)),
                        geo_id=geo_id,
                        geo_name=str(raw.get("locationname", geo_id)),
                        value=value,
                        unit=str(raw.get("data_value_unit", metric["unit"])) or metric["unit"],
                        source_name="CDC PLACES",
                        source_url=f"{url}?$where=stateabbr='{state_abbr}' AND year='{year}'",
                        retrieved_at=datetime.now(UTC),
                    )
                )
        if rows:
            rows.sort(key=lambda row: (row.year, row.geo_name))
            return rows[:limit]
    return []


def run_internet_research(query: str, limit: int = 200) -> ResearchResult:
    intent = parse_intent(query)
    metric = next((item for item in METRICS if item["key"] == intent.metric_key), METRICS[0])

    if metric["source"] == "cdc_places":
        items = _fetch_places_rows(intent, metric, limit)
    else:
        items = _fetch_census_rows(intent, metric, limit)

    source_map = _source_lookup()
    source_names = sorted({item.source_name for item in items})
    sources = [source_map.get(name, SourceAttributionRead(name=name, url="", citation="", category="")) for name in source_names]

    note = "Live internet retrieval from prioritized CHNA references."
    if not items:
        note = (
            "No rows were returned from prioritized sources for this exact query. "
            "Try a nearby year, remove strict geography wording, or ask for one of: "
            "per capita income, household income, population, diabetes, obesity."
        )

    return ResearchResult(
        query=query,
        intent=intent,
        items=items,
        sources=sources,
        note=note,
    )
