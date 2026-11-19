with gdansk as (
    select
        trip_id,
        arrival_time,
        departure_time,
        stop_id,
        stop_sequence::double as stop_sequence,
        'gdansk' as city,
        regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1)::date as snapshot_date
    from read_csv('../../data/static/gdansk/*/stop_times.txt', filename = true, all_varchar = true)
),

gdynia as (
    select
        trip_id,
        arrival_time,
        departure_time,
        stop_id,
        stop_sequence::double as stop_sequence,
        'gdynia' as city,
        regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1)::date as snapshot_date
    from read_csv('../../data/static/gdynia/*/stop_times.txt', filename = true, all_varchar = true)
)

select * from gdansk
union all
select * from gdynia