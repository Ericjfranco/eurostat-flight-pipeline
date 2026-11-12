from src.transform.jsonstat_to_dataframe import jsonstat_to_dataframe


def test_jsonstat_to_dataframe_expands_values():
    payload = {
        "class": "dataset", "id": ["geo", "time"], "size": [2, 2],
        "dimension": {
            "geo": {"category": {"index": {"DE": 0, "FR": 1},
                                   "label": {"DE": "Germany", "FR": "France"}}},
            "time": {"category": {"index": {"2023-01": 0, "2023-02": 1},
                                    "label": {"2023-01": "Jan 2023", "2023-02": "Feb 2023"}}},
        },
        "value": {"0": 10, "1": 11, "2": 20, "3": 21},
    }
    df = jsonstat_to_dataframe(payload)
    assert len(df) == 4
    assert df.iloc[0]["geo"] == "DE"
    assert df.iloc[0]["time"] == "2023-01"
    assert df.iloc[0]["value"] == 10
