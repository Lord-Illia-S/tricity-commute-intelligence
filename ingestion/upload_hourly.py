import io
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

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
WARSAW = ZoneInfo("Europe/Warsaw")


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


def hhmm_to_utc(hhmm: str, ref: datetime) -> datetime:
    hour, minutes = hhmm.split(":")
    t = ref.replace(hour=int(hour), minute=int(minutes), second=0)
    if t - ref < -timedelta(hours=12):
        t += timedelta(days=1)
    if t - ref > timedelta(hours=12):
        t -= timedelta(days=1)
    return t.astimezone(timezone.utc)


def gdynia_to_table(files):
    rows = []
    for file in files:
        data = json.loads(file.read_text(encoding="utf-8"))
        fetched_at = datetime.strptime(file.parent.name + file.stem, "%Y%m%d%H%M%SZ").replace(
            tzinfo=timezone.utc
        )
        for stop_id, stop_data in data.items():
            ref = datetime.strptime(stop_data["lastUpdate"], "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=WARSAW
            )
            for d in stop_data.get("delay", []):
                rows.append(
                    {
                        "stop_id": stop_id,
                        "trip_id": d.get("trip"),
                        "route_id": d.get("routeId"),
                        "vehicle_id": d.get("vehicleId"),
                        "delay_seconds": d.get("delayInSeconds"),
                        "status": d.get("status"),
                        "theoretical_at": hhmm_to_utc(d["theoreticalTime"], ref),
                        "estimated_at": hhmm_to_utc(d["estimatedTime"], ref),
                        "last_update": ref.astimezone(timezone.utc),
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


def pending_hours(base_dir, ext, now):
    hours = set()
    current_hour = now.replace(minute=0, second=0, microsecond=0)
    for file in base_dir.glob("*/*" + ext):
        file_name = file.parent.name + file.stem[:2]
        parsed_file = datetime.strptime(file_name, "%Y%m%d%H").replace(tzinfo=timezone.utc)
        if parsed_file < current_hour:
            hours.add(parsed_file)
    return sorted(hours)


FEEDS = [
    ("gdansk", Path("data/raw/gdansk"), ".json", to_table),
    ("gdansk_trip_updates", Path("data/raw/gdansk_trip_updates"), ".pb", trip_updates_to_table),
    ("gdynia", Path("data/raw/gdynia"), ".json", gdynia_to_table),
]

if __name__ == "__main__":
    now = datetime.now(timezone.utc)
    for name, base_dir, ext, parse in FEEDS:
        for hour in pending_hours(base_dir, ext, now):
            files = files_for_hour(base_dir, hour, ext)
            upload(parse(files), hour, name)
            for f in files:
                f.unlink()
