select city, stop_id, snapshot_date, count(*) as n
from {{ ref('stg_stops') }}
group by city, stop_id, snapshot_date
having count(*) > 1