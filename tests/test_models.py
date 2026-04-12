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

    # 4. Active (today, current time between start and end)
    base_now = datetime.now()
    today = base_now.date()
    start_time = (base_now - timedelta(minutes=30)).time()
    # Ensure end_time is on the same day if possible, or just use a safe offset
    end_time = (base_now + timedelta(minutes=30)).time()
    
    # We need to handle the case where adding 30 mins rolls over to next day
    if (base_now + timedelta(minutes=30)).date() > today:
        # If it rolls over, just set end_time to max to stay on same day for test
        end_time = time(23, 59, 59)

    z4 = Zawody(nazwa="Trwające", data=today, godzina_start=start_time, godzina_koniec=end_time, dyscyplina_id=d.id)
    assert z4.computed_status == "w_trakcie"

    # 5. Finished (today, but end time passed)
    past_time = (datetime.now() - timedelta(minutes=5)).time()
    z5 = Zawody(nazwa="Skończone dziś", data=today, godzina_koniec=past_time, dyscyplina_id=d.id)
    assert z5.computed_status == "zakonczone"
