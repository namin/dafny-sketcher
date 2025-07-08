datatype Day = Sunday | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday

// next_biz_day: Returns the next business day.
function next_biz_day(d: Day): Day

// iter_biz_day: Iterates the next business day function n times.
function iter_biz_day(d: Day, n: nat): Day

// iter5_biz_day_idempotent: Taking the next five business days, starting from a business day, is idempotent.
lemma {:axiom} iter5_biz_day_idempotent(d: Day)
requires d != Sunday && d != Saturday
ensures iter_biz_day(d, 5) == d
