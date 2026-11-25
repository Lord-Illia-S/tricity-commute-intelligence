import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

GDYNIA_URL = "https://api.zdiz.gdynia.pl/pt/delays"
GDYNIA_STOPS = [
    35111,
    35200,
    39440,
    37410,
    36040,
    35080,
    36120,
    37050,
    35250,
    37460,
    36080,
    35112,
    35270,
    37040,
    37060,
    37090,
    37420,
    37440,
    36050,
    37450,
    37470,
    35040,
    35260,
    33190,
    35170,
    36150,
    33090,
    37400,
    36340,
    36360,
    33170,
    33180,
    33080,
    35070,
    37130,
    36310,
    36330,
    36390,
    36140,
    35090,
]
log = logging.getLogger(__name__)


def fetch_gdynia() -> dict:
    result = {}
    for stop in GDYNIA_STOPS:
        try:
            r = requests.get(GDYNIA_URL, params={"stopId": stop}, timeout=10)
            r.raise_for_status()
            result[str(stop)] = r.json()
        except requests.RequestException as e:
            log.warning("Gdynia stop %s failed: %s", stop, e)
        time.sleep(0.2)
    return result


def save_raw(data: dict, base: Path = Path("data/raw/gdynia")) -> Path:
    now = datetime.now(timezone.utc)
    folder = base / now.strftime("%Y%m%d")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (now.strftime("%H%M%SZ") + ".json")
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return path


if __name__ == "__main__":
    data = fetch_gdynia()
    path = save_raw(data)
    print(len(data), "stops saved to", path)
