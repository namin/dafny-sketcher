datatype Day = Sunday | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday

function next_biz_day(d: Day): Day
{
  match d
  case Monday => Tuesday
  case Tuesday => Wednesday
  case Wednesday => Thursday
  case Thursday => Friday
  case Friday => Monday
  case Saturday => Monday
  case Sunday => Monday
}

function iter_biz_day(d: Day, n: nat): Day
  decreases n
{
  if n == 0 then d
  else iter_biz_day(next_biz_day(d), n - 1)
}

lemma iter5_biz_day_idempotent(d: Day)
  requires d != Saturday && d != Sunday
  ensures iter_biz_day(d, 5) == iter_biz_day(iter_biz_day(d, 5), 5)
{
  // 5 business days from any weekday brings you to the same weekday next week
  match d
  case Monday =>
    assert iter_biz_day(Monday, 1) == Tuesday;
    assert iter_biz_day(Monday, 2) == Wednesday;
    assert iter_biz_day(Monday, 3) == Thursday;
    assert iter_biz_day(Monday, 4) == Friday;
    assert iter_biz_day(Monday, 5) == Monday;
    assert iter_biz_day(Monday, 5) == Monday;
    assert iter_biz_day(iter_biz_day(Monday, 5), 5) == iter_biz_day(Monday, 5);
  case Tuesday =>
    assert iter_biz_day(Tuesday, 1) == Wednesday;
    assert iter_biz_day(Tuesday, 2) == Thursday;
    assert iter_biz_day(Tuesday, 3) == Friday;
    assert iter_biz_day(Tuesday, 4) == Monday;
    assert iter_biz_day(Tuesday, 5) == Tuesday;
  case Wednesday =>
    assert iter_biz_day(Wednesday, 1) == Thursday;
    assert iter_biz_day(Wednesday, 2) == Friday;
    assert iter_biz_day(Wednesday, 3) == Monday;
    assert iter_biz_day(Wednesday, 4) == Tuesday;
    assert iter_biz_day(Wednesday, 5) == Wednesday;
  case Thursday =>
    assert iter_biz_day(Thursday, 1) == Friday;
    assert iter_biz_day(Thursday, 2) == Monday;
    assert iter_biz_day(Thursday, 3) == Tuesday;
    assert iter_biz_day(Thursday, 4) == Wednesday;
    assert iter_biz_day(Thursday, 5) == Thursday;
  case Friday =>
    assert iter_biz_day(Friday, 1) == Monday;
    assert iter_biz_day(Friday, 2) == Tuesday;
    assert iter_biz_day(Friday, 3) == Wednesday;
    assert iter_biz_day(Friday, 4) == Thursday;
    assert iter_biz_day(Friday, 5) == Friday;
}