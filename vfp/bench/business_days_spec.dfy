datatype Day = Sunday | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday

function next_biz_day(d: Day): Day

function iter_biz_day(d: Day, n: nat): Day

lemma {:axiom} iter5_biz_day_idempotent(d: Day)
  requires d != Saturday && d != Sunday
  ensures iter_biz_day(d, 5) == iter_biz_day(iter_biz_day(d, 5), 5)