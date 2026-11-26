select city, trip_id, stop_sequence, snapshot_date, count(*) as n
from {{ ref('stg_stop_times') }}
group by city, trip_id, stop_sequence, snapshot_date
having count(*) > 1
