import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

from ingestion import gdynia
from ingestion.gdynia import save_raw
from ingestion.upload_hourly import gdynia_to_table, hhmm_to_utc

WARSAW = ZoneInfo("Europe/Warsaw")


def test_hhmm_normal_case():
    ref = datetime(2026, 11, 25, 20, 0, tzinfo=WARSAW)
    assert hhmm_to_utc("20:37", ref) == datetime(2026, 11, 25, 19, 37, tzinfo=timezone.utc)


def test_hhmm_after_midnight():
    ref = datetime(2026, 11, 25, 23, 58, tzinfo=WARSAW)
    assert hhmm_to_utc("00:05", ref) == datetime(2026, 11, 25, 23, 5, tzinfo=timezone.utc)


def test_hhmm_before_midnight():
    ref = datetime(2026, 11, 26, 0, 2, tzinfo=WARSAW)
    assert hhmm_to_utc("23:55", ref) == datetime(2026, 11, 25, 22, 55, tzinfo=timezone.utc)


def test_save_raw_writes_json(tmp_path):
    data = {"35111": {"delay": []}}
    path = save_raw(data, base=tmp_path)
    assert path.exists()
    assert path.name.endswith("Z.json")
    assert json.loads(path.read_text(encoding="utf-8")) == data


def test_gdynia_to_table(tmp_path):
    folder = tmp_path / "20261125"
    folder.mkdir()
    file = folder / "191443Z.json"
    sample = {
        "35111": {
            "lastUpdate": "2026-11-25 20:11:52",
            "delay": [
                {
                    "trip": 6195772,
                    "routeId": 10147,
                    "vehicleId": 203949,
                    "delayInSeconds": 179,
                    "status": "REALTIME",
                    "theoreticalTime": "20:10",
                    "estimatedTime": "20:12",
                }
            ],
        }
    }
    file.write_text(json.dumps(sample), encoding="utf-8")

    table = gdynia_to_table([file])
    row = table.to_pylist()[0]

    assert table.num_rows == 1
    assert row["stop_id"] == "35111"
    assert row["delay_seconds"] == 179
    assert row["theoretical_at"] == datetime(2026, 11, 25, 19, 10, tzinfo=timezone.utc)
    assert row["fetched_at"] == datetime(2026, 11, 25, 19, 14, 43, tzinfo=timezone.utc)


def test_fetch_gdynia_survives_errors(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("API down")

    monkeypatch.setattr(gdynia, "GDYNIA_STOPS", [1, 2])
    monkeypatch.setattr(gdynia.requests, "get", fake_get)
    monkeypatch.setattr(gdynia.time, "sleep", lambda s: None)

    assert gdynia.fetch_gdynia() == {}
