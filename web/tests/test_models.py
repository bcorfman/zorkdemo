import datetime
from web.models import AdventureStore


def test_adventure_store_model_create():
    astore = AdventureStore.create(
        session_id="1234",
        save_data="abcdef",
    )
    assert AdventureStore.select().count() == 1
    assert isinstance(astore.create_ts, datetime.datetime)
    assert isinstance(astore.updated_ts, datetime.datetime)


def test_adventure_store_model_json():
    astore = AdventureStore.create(
        session_id="1234",
        save_data="abcdef",
    )
    assert astore.to_json() == {
        "session_id": "1234",
        "save_data": "abcdef",
        "create_ts": astore.create_ts.isoformat(),
        "updated_ts": astore.updated_ts.isoformat(),
    }

