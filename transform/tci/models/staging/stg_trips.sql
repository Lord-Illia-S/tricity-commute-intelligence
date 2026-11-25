with gdansk as (
    select
        route_id,
        service_id,
        trip_id,
        trip_headsign,
        direction_id::double as direction_id,
        'gdansk' as city,
        regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1)::date as snapshot_date
    from read_csv('../../data/static/gdansk/*/trips.txt', filename = true, all_varchar = true)
),

gdynia as (
    select
        route_id,
        service_id,
        trip_id,
        trip_headsign,
        direction_id::double as direction_id,
        'gdynia' as city,
        regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1)::date as snapshot_date
    from read_csv('../../data/static/gdynia/*/trips.txt', filename = true, all_varchar = true)
)

select * from gdansk
union all
select * from gdynia
