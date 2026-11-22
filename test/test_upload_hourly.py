from datetime import datetime, timezone

from google.transit import gtfs_realtime_pb2

from ingestion.upload_hourly import pending_hours, trip_updates_to_table


def test_pending_hours_skips_current_and_dedupes(tmp_path):
    for name in [
        "20261120/090000Z.pb",
        "20261120/091520Z.pb",
        "20261120/100000Z.pb",
        "20261120/110500Z.pb",
    ]:
        f = tmp_path / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.touch()
    now = datetime(2026, 11, 20, 11, 30, tzinfo=timezone.utc)
    assert pending_hours(tmp_path, ".pb", now) == [
        datetime(2026, 11, 20, 9, 00, tzinfo=timezone.utc),
        datetime(2026, 11, 20, 10, 00, tzinfo=timezone.utc),
    ]


def test_trip_updates_to_table(tmp_path):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    entity = feed.entity.add(id="1")
    entity.trip_update.trip.trip_id = "T1"
    stu = entity.trip_update.stop_time_update.add(stop_id="S1", stop_sequence=3)
    stu.arrival.delay = 120

    file_name = tmp_path / "20261120" / "090000Z.pb"
    file_name.parent.mkdir(parents=True, exist_ok=True)
    file_name.write_bytes(feed.SerializeToString())

    table = trip_updates_to_table([file_name])
    row = table.to_pylist()[0]
    assert table.num_rows == 1
    assert row["trip_id"] == "T1"
    assert row["stop_id"] == "S1"
    assert row["arrival_delay"] == 120
    assert row["fetched_at"] == datetime(2026, 11, 20, 9, 00, tzinfo=timezone.utc)
