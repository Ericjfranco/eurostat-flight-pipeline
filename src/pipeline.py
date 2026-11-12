from src.extract.extract_eurostat import extract
from src.transform.transform_eurostat import transform
from src.load.load_postgres import load


def run_pipeline():
    raw_file = extract()
    csv_file = transform(raw_file)
    loaded = load(csv_file)
    return {"raw_file": raw_file, "csv_file": csv_file, "loaded": loaded}


if __name__ == "__main__":
    print(run_pipeline())
