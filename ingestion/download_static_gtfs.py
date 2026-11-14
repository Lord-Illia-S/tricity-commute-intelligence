from datetime import date
from pathlib import Path

import requests


def download_gtfs(base_dir=Path("data/static")):
    sources: dict[str, str] = {
        "gdansk": "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/30e783e4-2bec-4a7d-bb22-ee3e3b26ca96/download/gtfsgoogle.zip",
        "gdynia": "https://api.zdiz.gdynia.pl/pt/gtfs.zip",
        "skm": "https://www.skm.pkp.pl/gtfs-mi-kpd.zip",
    }

    today = date.today()
    file_date = today.isoformat()
    for origin, url in sources.items():
        file_name = Path(base_dir) / origin / file_date / "gtfs.zip"
        if file_name.exists() and file_name.stat().st_size > 0:
            print(f"File {file_name} already exists")
        else:
            try:
                response_gtfs = requests.get(url, timeout=20)
                response_gtfs.raise_for_status()
                file_name.parent.mkdir(parents=True, exist_ok=True)
                file_name.write_bytes(response_gtfs.content)
            except requests.exceptions.RequestException as error:
                print(f"{origin}: URL failed ({error}), skipping")


if __name__ == "__main__":
    download_gtfs()
