import io
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
import dotenv
import pyarrow
import pyarrow.parquet as pq

dotenv.load_dotenv()

ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")


def files_for_hour(base_dir: Path, hour: datetime):
    folder = base_dir / hour.strftime("%Y%m%d")
    return sorted(folder.glob(hour.strftime("%H") + "*.json"))


def to_table(files):
    rows = []
    for file in files:
        data = json.loads(file.read_text(encoding="utf-8"))
        fetched_at = datetime.strptime(file.parent.name + file.stem, "%Y%m%d%H%M%SZ").replace(
            tzinfo=timezone.utc
        )
        for vehicle in data["vehicles"]:
            vehicle["fetched_at"] = fetched_at
            rows.append(vehicle)

    return pyarrow.Table.from_pylist(rows)


def upload(table, hour):
    buf = io.BytesIO()
    pq.write_table(table, buf)
    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )
    key = f"dt={hour:%Y-%m-%d}/hour={hour:%H}/gdansk.parquet"
    s3.put_object(Bucket=R2_BUCKET, Key=key, Body=buf.getvalue())


if __name__ == "__main__":
    hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) - timedelta(
        hours=1
    )
    files = files_for_hour(Path("data/raw/gdansk"), hour)
    if len(files) == 0:
        print(f"No files found for hour {hour:%Y-%m-%d %H}:00 UTC")
    else:
        upload(to_table(files), hour)
        for f in files:
            f.unlink()
