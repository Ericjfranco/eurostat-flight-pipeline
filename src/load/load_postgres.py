import json
import logging
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values, Json
from src.config import DATASET, DB_CONFIG, PROCESSED_DIR, PROJECT_ROOT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
SCHEMA_FILE = PROJECT_ROOT / "sql" / "schema.sql"


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def ensure_schema(conn):
    with conn.cursor() as cur:
        cur.execute(SCHEMA_FILE.read_text(encoding="utf-8"))
    conn.commit()


def load(csv_file: str | None = None) -> int:
    if csv_file is None:
        csv_file = str(PROCESSED_DIR / f"{DATASET}_processed.csv")
    df = pd.read_csv(csv_file)
    if df.empty:
        raise ValueError("CSV tratado está vazio.")
    rows = []
    for row in df.to_dict(orient="records"):
        rows.append((
            row["dataset_code"], str(row["period"]), str(row.get("geo_code") or "UNKNOWN"),
            row.get("geo_label"), row.get("unit_code"), row.get("unit_label"), float(row["value"]),
            Json(
                json.loads(row["dimensions"])
                if isinstance(row["dimensions"], str)
                else {}
            ),
            Json(
                json.loads(row["dimension_labels_json"])
                if isinstance(row["dimension_labels_json"], str)
                else {}
            ),
            row.get("source_updated"),
        ))
    sql = """
      INSERT INTO fact_air_traffic
      (dataset_code, period, geo_code, geo_label, unit_code, unit_label, value,
       dimensions, dimension_labels, source_updated) VALUES %s
      ON CONFLICT (dataset_code, period, geo_code, dimensions) DO UPDATE SET
       geo_label=EXCLUDED.geo_label, unit_code=EXCLUDED.unit_code,
       unit_label=EXCLUDED.unit_label, value=EXCLUDED.value,
       dimension_labels=EXCLUDED.dimension_labels,
       source_updated=EXCLUDED.source_updated, loaded_at=NOW()
    """
    with get_connection() as conn:
        ensure_schema(conn)
        with conn.cursor() as cur:
            execute_values(cur, sql, rows, page_size=1000)
        conn.commit()
    logger.info("%s registros inseridos/atualizados.", len(rows))
    return len(rows)


if __name__ == "__main__":
    print(f"Registros carregados: {load()}")
