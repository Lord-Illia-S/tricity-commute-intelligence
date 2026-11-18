import io
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
import dotenv
import pyarrow.parquet as pq

dotenv.load_dotenv()

ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")
EXPECTED_FEEDS = ["gdansk"]


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
    failed = False
    for feed in EXPECTED_FEEDS:
        count = rows.get(feed, 0)
        if count == 0:
            print(f"ALERT: {feed} has 0 rows on {day:%Y-%m-%d}")
            failed = True
        else:
            print(f"{day:%Y-%m-%d} {feed}: {count} rows")

    if failed:
        sys.exit(1)
