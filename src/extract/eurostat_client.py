import logging
import requests

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
logger = logging.getLogger(__name__)


def fetch_dataset(dataset_code: str, language: str = "EN", last_periods: int = 0) -> dict:
    """Consulta a Statistics API e retorna o JSON-stat recebido."""
    url = f"{BASE_URL}/{dataset_code}"
    params = {"lang": language}
    if last_periods and last_periods > 0:
        params["lastTimePeriod"] = last_periods
    response = requests.get(
        url, params=params,
        headers={"User-Agent": "eurostat-flight-data-pipeline/1.0"},
        timeout=(15, 180),
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"Eurostat retornou erro: {payload['error']}")
    if payload.get("class") != "dataset" or not payload.get("id") or not payload.get("size"):
        raise ValueError(f"Resposta JSON-stat inesperada para {dataset_code}")
    logger.info("Dataset %s recebido; atualizado em %s", dataset_code, payload.get("updated"))
    return payload
