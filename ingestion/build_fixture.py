from pathlib import Path

import duckdb

from ingestion.upload_hourly import gdynia_to_table, to_table, trip_updates_to_table

OUT = Path("test/fixtures/tci_sample.duckdb")
DAY = "20261127"

LIVE = [
    ("raw_gdansk_vehicles", Path("data/raw/gdansk"), ".json", to_table),
    ("raw_gdansk_trip_updates", Path("data/raw/gdansk_trip_updates"), ".pb", trip_updates_to_table),
    ("raw_gdynia_delays", Path("data/raw/gdynia"), ".json", gdynia_to_table),
]
STATIC = Path("data/static")


def csv(snap, f):
    return f"read_csv('{(snap / f).as_posix()}', all_varchar = true)"


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.unlink(missing_ok=True)
    con = duckdb.connect(str(OUT))

    for name, base, ext, parse in LIVE:
        files = sorted((base / DAY).glob("*" + ext))
        arrow_table = parse(files)
        con.execute(f"create table {name} as select * from arrow_table")
        print(name, arrow_table.num_rows)

    for city in ["gdansk", "gdynia"]:
        snap = sorted((STATIC / city).iterdir())[-1]

        con.execute(
            f"create or replace temp view r as select * from {csv(snap, 'routes.txt')} limit 5"
        )
        con.execute(f"create table raw_{city}_routes as select * from r")
        con.execute(
            f"create table raw_{city}_trips as select * from {csv(snap, 'trips.txt')} "
            f"where route_id in (select route_id from r)"
        )
        con.execute(
            f"create table raw_{city}_stop_times "
            f"as select * from {csv(snap, 'stop_times.txt')}"
            f" where trip_id in (select trip_id from raw_{city}_trips)"
        )
        con.execute(
            f"create table raw_{city}_stops as select * from {csv(snap, 'stops.txt')}"
            f" where stop_id in (select stop_id from raw_{city}_stop_times)"
        )
        print(city, snap.name)

    con.close()
