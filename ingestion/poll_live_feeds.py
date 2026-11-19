import time
from datetime import datetime, timezone
from pathlib import Path

import requests

FEEDS = [
    ("https://ckan2.multimediagdansk.pl/gpsPositions?v=2", Path("data/raw/gdansk"), ".json"),
    (
        "https://ckan2.multimediagdansk.pl/gtfs-rt?feed=tripUpdates",
        Path("data/raw/gdansk_trip_updates"),
        ".pb",
    ),
]


def fetch_and_save(url: str, base_dir: Path, now: datetime, ext: str = ".json") -> Path:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    download_path = base_dir / now.strftime("%Y%m%d") / (now.strftime("%H%M%SZ") + ext)
    download_path.parent.mkdir(parents=True, exist_ok=True)
    with open(download_path, "wb") as f:
        f.write(response.content)
    return download_path


if __name__ == "__main__":
    wait = 20.0

    while True:
        try:
            now = datetime.now(timezone.utc)
            failed = False
            for url, base_dir, ext in FEEDS:
                try:
                    fetch_and_save(url, base_dir, now, ext)
                except requests.RequestException as e:
                    print(e)
                    failed = True

            wait = min(wait * 2, 300) if failed else 20.0
            time.sleep(wait)
        except KeyboardInterrupt:
            break
