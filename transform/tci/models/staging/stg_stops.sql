with gdansk as (
    select
        stop_id,
        stop_name,
        stop_lat::double as stop_lat,
        stop_lon::double as stop_lon,
        'gdansk' as city,
        regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1)::date as snapshot_date
    from read_csv('../../data/static/gdansk/*/stops.txt', filename = true, all_varchar = true)
),

gdynia as (
    select
        stop_id,
        stop_name,
        stop_lat::double as stop_lat,
        stop_lon::double as stop_lon,
        'gdynia' as city,
        regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1)::date as snapshot_date
    from read_csv('../../data/static/gdynia/*/stops.txt', filename = true, all_varchar = true)
)

select * from gdansk
union all
select * from gdynia
