drop function loop_test(timestamp(6) without time zone,timestamp(6) without time zone);
create or replace function loop_test(
    start_time timestamp without time zone,
    end_time timestamp without time zone)
    returns setof text as # setof record
$$
declare
    i timestamp without time zone;
    result record;
begin
    i := start_time;
    while i < end_time loop
        with cycles_cte as (
            select *, lead(arrival, 1) over (partition by scheduleid order by arrival) nextarrive
            /*to obtain arrival time of next row (i.e cycle) */
             from cycles order by scheduleid, arrival)
          select * from cycles_cte
          where depart < i and nextarrive > i;
          i := i + '00:05:00'::interval;
          return next result;
          raise notice 'iteration %', i;
    end loop;
    return;
    end
$$ language plpgsql;

select * from loop_test('2019-01-01 04:00:00', '2019-01-01 23:45:00') as
tm(scheduleid numeric,cycle integer, s_eng varchar, d_eng varchar, arrival timestamp(6) without time zone, depart timestamp(6) without time zone, nextarrive timestamp without time zone);
