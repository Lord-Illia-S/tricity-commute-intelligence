import io
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
import dotenv
import pyarrow
import pyarrow.parquet as pq
from google.transit import gtfs_realtime_pb2

dotenv.load_dotenv()

ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")


def files_for_hour(base_dir: Path, hour: datetime, ext: str = ".json"):
    folder = base_dir / hour.strftime("%Y%m%d")
    return sorted(folder.glob(hour.strftime("%H") + "*" + ext))


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


def trip_updates_to_table(files):
    rows = []
    for file in files:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(file.read_bytes())
        fetched_at = datetime.strptime(file.parent.name + file.stem, "%Y%m%d%H%M%SZ").replace(
            tzinfo=timezone.utc
        )
        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue
            tu = entity.trip_update
            for stu in tu.stop_time_update:
                rows.append(
                    {
                        "trip_id": tu.trip.trip_id,
                        "route_id": tu.trip.route_id,
                        "stop_id": stu.stop_id,
                        "stop_sequence": stu.stop_sequence,
                        "arrival_delay": stu.arrival.delay,
                        "departure_delay": stu.departure.delay,
                        "fetched_at": fetched_at,
                    }
                )

    return pyarrow.Table.from_pylist(rows)


def upload(table, hour, feed):
    buf = io.BytesIO()
    pq.write_table(table, buf)
    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )
    key = f"dt={hour:%Y-%m-%d}/hour={hour:%H}/{feed}.parquet"
    s3.put_object(Bucket=R2_BUCKET, Key=key, Body=buf.getvalue())


FEEDS = [
    ("gdansk", Path("data/raw/gdansk"), ".json", to_table),
    ("gdansk_trip_updates", Path("data/raw/gdansk_trip_updates"), ".pb", trip_updates_to_table),
]

if __name__ == "__main__":
    hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) - timedelta(
        hours=1
    )

    for name, base_dir, ext, parse in FEEDS:
        files = files_for_hour(base_dir, hour, ext)
        if len(files) == 0:
            print(f"{name}: No files found for hour {hour:%Y-%m-%d %H}:00 UTC")
        else:
            upload(parse(files), hour, name)
            for f in files:
                f.unlink()
