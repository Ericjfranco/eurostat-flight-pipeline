import json
import logging
from datetime import datetime, timezone
from src.config import DATASET, LANGUAGE, LAST_PERIODS, RAW_DIR
from src.extract.eurostat_client import fetch_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract() -> str:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    payload = fetch_dataset(DATASET, LANGUAGE, LAST_PERIODS)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = RAW_DIR / f"{DATASET}_{stamp}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    logger.info("Arquivo bruto salvo em %s", output)
    return str(output)


if __name__ == "__main__":
    print(extract())
