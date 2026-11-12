import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET = os.getenv("EUROSTAT_DATASET", "ttr00017")
LANGUAGE = os.getenv("EUROSTAT_LANGUAGE", "EN")
LAST_PERIODS = int(os.getenv("EUROSTAT_LAST_PERIODS", "3"))
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DB_CONFIG = {
    "host": os.getenv("DATA_DB_HOST", "localhost"),
    "port": int(os.getenv("DATA_DB_PORT", "5432")),
    "dbname": os.getenv("DATA_DB_NAME", "flight_data"),
    "user": os.getenv("DATA_DB_USER", "pipeline"),
    "password": os.getenv("DATA_DB_PASSWORD", "pipeline_dev"),
}
