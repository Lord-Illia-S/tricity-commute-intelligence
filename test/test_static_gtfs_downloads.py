from datetime import date
from unittest.mock import MagicMock, patch

from ingestion.download_static_gtfs import download_gtfs


def test_download_static_gtfs(tmp_path):
    test_response = MagicMock()
    test_response.content = b"test text fro staatic gtfs download"

    with patch(
        "ingestion.download_static_gtfs.requests.get", return_value=test_response
    ) as mock_get:
        download_gtfs(base_dir=tmp_path)
        today = date.today()
        file_date = today.isoformat()

        assert mock_get.call_count == 3

        for origin in ("gdansk", "gdynia", "skm"):
            file_path = tmp_path / origin / file_date / "gtfs.zip"
            assert file_path.exists()
            assert file_path.read_bytes() == test_response.content

        download_gtfs(base_dir=tmp_path)
        assert mock_get.call_count == 3
