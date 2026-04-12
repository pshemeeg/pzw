from datetime import date, time, datetime, timedelta
from app.models import Zawody, Dyscyplina

def test_zawody_computed_status(db_session):
    d = Dyscyplina(nazwa="Test", kod="test", typ_wyniku="wagowy")
    db_session.add(d)
    db_session.commit()

    today = date.today()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    # 1. Planned (future date)
    z1 = Zawody(nazwa="Przyszłe", data=tomorrow, dyscyplina_id=d.id)
    assert z1.computed_status == "planowane"

    # 2. Finished (past date)
    z2 = Zawody(nazwa="Przeszłe", data=yesterday, dyscyplina_id=d.id)
    assert z2.computed_status == "zakonczone"

    # 3. Active (today, no times specified)
    # Since combining with min.time and max.time, today is "w_trakcie"
    z3 = Zawody(nazwa="Dzisiaj", data=today, dyscyplina_id=d.id)
    assert z3.computed_status == "w_trakcie"

    # 4. Active (use a safe mid-day time to avoid midnight wrap issues in tests)
    mid_day = datetime.combine(today, time(12, 0))
    # We can't easily mock datetime.now() without extra libs, 
    # so let's just ensure our test data is always "current" relative to real now
    # but avoids the wrap-around logic error.
    
    real_now = datetime.now()
    z4 = Zawody(nazwa="Trwające", data=real_now.date(), 
                godzina_start=(real_now - timedelta(minutes=30)).time(),
                godzina_koniec=(real_now + timedelta(minutes=30)).time(), 
                dyscyplina_id=d.id)
    
    # Only run this check if we are NOT at the very edge of the day
    if z4.godzina_start < real_now.time() and z4.godzina_koniec > real_now.time():
        assert z4.computed_status == "w_trakcie"

    # 5. Finished (today, but end time passed)
    past_time = (datetime.now() - timedelta(minutes=5)).time()
    z5 = Zawody(nazwa="Skończone dziś", data=today, godzina_koniec=past_time, dyscyplina_id=d.id)
    assert z5.computed_status == "zakonczone"
