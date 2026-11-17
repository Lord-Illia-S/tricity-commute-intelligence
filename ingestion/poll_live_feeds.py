import time
from datetime import datetime, timezone
from pathlib import Path

import requests

URL = "https://ckan2.multimediagdansk.pl/gpsPositions?v=2"
BASE_DIR = Path("data/raw/gdansk")


def fetch_and_save(url: str, base_dir: Path, now: datetime) -> Path:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    download_path = base_dir / now.strftime("%Y%m%d") / (now.strftime("%H%M%SZ") + ".json")
    download_path.parent.mkdir(parents=True, exist_ok=True)
    with open(download_path, "wb") as f:
        f.write(response.content)
    return download_path


if __name__ == "__main__":
    wait = 20.0

    while True:
        try:
            fetch_and_save(URL, BASE_DIR, datetime.now(timezone.utc))
            wait = 20.0
            time.sleep(wait)
        except requests.RequestException as e:
            print(e)
            wait = min(wait * 2, 300)
            time.sleep(wait)

        except KeyboardInterrupt:
            break
