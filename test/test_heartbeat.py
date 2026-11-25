from datetime import datetime, timezone

from ingestion.heartbeat import check_feeds

day = datetime(2026, 11, 20, tzinfo=timezone.utc)


def test_heartbeat():
    expected = ["gdansk", "gdansk_trip_updates"]
    assert check_feeds({"gdansk": 500}, expected, day) == ["gdansk_trip_updates"]
    assert check_feeds({"gdansk": 5, "gdansk_trip_updates": 7}, expected, day) == []
