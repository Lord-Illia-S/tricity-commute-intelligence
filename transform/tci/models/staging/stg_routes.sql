with gdansk as (
    select
        route_id,
        route_short_name,
        route_long_name,
        route_type::double as route_type,
        'gdansk' as city,
        regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1)::date as snapshot_date
    from read_csv('../../data/static/gdansk/*/routes.txt', filename = true, all_varchar = true)
),

gdynia as (
    select
        route_id,
        route_short_name,
        route_long_name,
        route_type::double as route_type,
        'gdynia' as city,
        regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1)::date as snapshot_date
    from read_csv('../../data/static/gdynia/*/routes.txt', filename = true, all_varchar = true)
)

select * from gdansk
union all
select * from gdynia