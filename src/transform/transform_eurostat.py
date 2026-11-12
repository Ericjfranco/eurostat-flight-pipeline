import json
import logging
from pathlib import Path
import pandas as pd
from src.config import DATASET, RAW_DIR, PROCESSED_DIR
from src.transform.jsonstat_to_dataframe import jsonstat_to_dataframe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def transform(raw_file: str | None = None) -> str:
    if raw_file is None:
        candidates = sorted(RAW_DIR.glob(f"{DATASET}_*.json"))
        if not candidates:
            raise FileNotFoundError("Nenhum JSON bruto encontrado. Execute a extração.")
        raw_file = str(candidates[-1])
    payload = json.loads(Path(raw_file).read_text(encoding="utf-8"))
    df = jsonstat_to_dataframe(payload)
    if df.empty:
        raise ValueError("A API retornou zero observações com valor.")

    time_col = "time" if "time" in df.columns else "TIME_PERIOD" if "TIME_PERIOD" in df.columns else None
    if not time_col:
        raise ValueError(f"Dimensão temporal não encontrada: {list(df.columns)}")
    df["period"] = df[time_col].astype(str)
    geo_col = "geo" if "geo" in df.columns else "airport" if "airport" in df.columns else None
    df["geo_code"] = df[geo_col].astype(str) if geo_col else "UNKNOWN"
    labels = df["dimension_labels"].apply(lambda x: x if isinstance(x, dict) else {})
    df["geo_label"] = labels.apply(lambda x: x.get("geo") or x.get("airport"))
    df["unit_code"] = df["unit"].astype(str) if "unit" in df.columns else None
    df["unit_label"] = labels.apply(lambda x: x.get("unit"))
    df["dataset_code"] = DATASET
    df["source_updated"] = payload.get("updated")

    excluded = {"value", "status", "dimension_labels", "period", "geo_code", "geo_label",
                "unit_code", "unit_label", "dataset_code", "source_updated"}
    dimension_cols = [c for c in df.columns if c not in excluded]
    df["dimensions"] = df[dimension_cols].apply(
        lambda row: json.dumps(row.to_dict(), ensure_ascii=False), axis=1
    )
    df["dimension_labels_json"] = df["dimension_labels"].apply(
        lambda x: json.dumps(x, ensure_ascii=False)
    )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value", "period"])
    df = df.drop_duplicates(subset=["dataset_code", "period", "geo_code", "dimensions"])
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output = PROCESSED_DIR / f"{DATASET}_processed.csv"
    df.to_csv(output, index=False)
    logger.info("%s registros preparados em %s", len(df), output)
    return str(output)


if __name__ == "__main__":
    print(transform())
