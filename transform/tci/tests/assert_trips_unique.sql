select city, trip_id, snapshot_date, count(*) as n
from {{ ref('stg_trips') }}
group by city, trip_id, snapshot_date
having count(*) > 1
