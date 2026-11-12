import itertools
import math
import pandas as pd


def _dimension_codes_and_labels(dimension: dict):
    category = dimension.get("category", {})
    index = category.get("index", {})
    if isinstance(index, list):
        codes = index
    else:
        codes = [code for code, _ in sorted(index.items(), key=lambda item: item[1])]
    labels_map = category.get("label", {})
    return codes, [labels_map.get(code, code) for code in codes]


def jsonstat_to_dataframe(payload: dict) -> pd.DataFrame:
    """Expande dimensões e vetor de valores JSON-stat em linhas tabulares."""
    dimension_ids = payload["id"]
    sizes = payload["size"]
    dimensions = payload["dimension"]
    values = payload.get("value", {})
    statuses = payload.get("status", {})
    codes_by_dim, labels_by_dim = [], []
    for dim_id in dimension_ids:
        codes, labels = _dimension_codes_and_labels(dimensions[dim_id])
        codes_by_dim.append(codes)
        labels_by_dim.append(labels)

    records = []
    for positions in itertools.product(*(range(size) for size in sizes)):
        flat_index = sum(
            position * math.prod(sizes[i + 1:])
            for i, position in enumerate(positions)
        )
        raw_value = values.get(str(flat_index)) if isinstance(values, dict) else (
            values[flat_index] if flat_index < len(values) else None
        )
        if raw_value is None:
            continue
        record, labels_record = {}, {}
        for i, dim_id in enumerate(dimension_ids):
            code = codes_by_dim[i][positions[i]]
            record[dim_id] = code
            labels_record[dim_id] = labels_by_dim[i][positions[i]]
        record["value"] = raw_value
        record["status"] = statuses.get(str(flat_index)) if isinstance(statuses, dict) else None
        record["dimension_labels"] = labels_record
        records.append(record)
    return pd.DataFrame.from_records(records)
