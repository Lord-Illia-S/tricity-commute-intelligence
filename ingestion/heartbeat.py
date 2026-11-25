import io
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
import dotenv
import pyarrow.parquet as pq

from ingestion.upload_hourly import FEEDS

dotenv.load_dotenv()

ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")
EXPECTED_FEEDS = [name for name, *_ in FEEDS]


def list_keys(s3, day):
    response = s3.list_objects_v2(Bucket=R2_BUCKET, Prefix=f"dt={day:%Y-%m-%d}/")
    contents = response.get("Contents", [])
    return [obj["Key"] for obj in contents]


def count_rows(s3, keys):
    rows = {}
    for key in keys:
        name = Path(key).stem
        data = s3.get_object(Bucket=R2_BUCKET, Key=key)["Body"].read()
        count = pq.read_metadata(io.BytesIO(data)).num_rows
        rows[name] = rows.get(name, 0) + count
    return rows


def check_feeds(rows, expected, day):
    empty_rows = []
    for feed in expected:
        count = rows.get(feed, 0)
        if count == 0:
            print(f"ALERT: {feed} has 0 rows on {day:%Y-%m-%d}")
            empty_rows.append(feed)
        else:
            print(f"{day:%Y-%m-%d} {feed}: {count} rows")
    return empty_rows


if __name__ == "__main__":
    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )

    day = datetime.now(timezone.utc) - timedelta(days=1)
    # day = datetime.now(timezone.utc)
    rows = count_rows(s3, list_keys(s3, day=day))

    empty_rows = check_feeds(rows, EXPECTED_FEEDS, day)

    if len(empty_rows) > 0:
        sys.exit(1)
