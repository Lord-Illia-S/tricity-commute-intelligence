select city, route_id, snapshot_date, count(*) as n
from {{ ref('stg_routes') }}
group by city, route_id, snapshot_date
having count(*) > 1
