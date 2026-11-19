from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from ingestion.poll_live_feeds import fetch_and_save


def test_fetch_and_save_writes_file(tmp_path):
    fake = MagicMock()
    fake.content = b'{"vehicles": []}'
    now = datetime(2026, 11, 15, 20, 0, 5, tzinfo=timezone.utc)

    with patch("ingestion.poll_live_feeds.requests.get", return_value=fake):
        path_json = fetch_and_save("https://example.com", tmp_path, now, ".json")
        path_pb = fetch_and_save("https://example.com", tmp_path, now, ".pb")

    assert path_json == tmp_path / "20261115" / "200005Z.json"
    assert path_pb == tmp_path / "20261115" / "200005Z.pb"

    assert path_json.read_bytes() == fake.content
    assert path_pb.read_bytes() == fake.content
