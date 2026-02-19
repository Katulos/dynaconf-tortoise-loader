import pytest
from dynaconf.utils.inspect import get_history

from dynaconf_tortoise_loader.tortoise_loader import delete, load, write


def test_write_tortoise_without_data(settings):
    with pytest.raises(AttributeError) as excinfo:
        write(settings)
    assert "Data must be provided" in str(excinfo.value)


def test_write_to_tortoise(settings):
    write(settings, {"SECRET": "tortoise_works"})
    load(settings, key="SECRET")
    assert settings.get("SECRET") == "tortoise_works"


def test_load_from_tortoise_with_key(settings):
    load(settings, key="SECRET")
    assert settings.get("SECRET") == "tortoise_works"


def test_write_and_load_from_tortoise_without_key(settings):
    write(settings, {"SECRET": "tortoise_works_perfectly"})
    load(settings)
    assert settings.get("SECRET") == "tortoise_works_perfectly"


def test_delete_from_tortoise(settings):
    write(settings, {"OTHER_SECRET": "tortoise_works"})
    load(settings)
    assert settings.get("OTHER_SECRET") == "tortoise_works"
    delete(settings, key="OTHER_SECRET")
    assert load(settings, key="OTHER_SECRET") is None


def test_delete_all_from_tortoise(settings):
    delete(settings)
    assert load(settings, key="OTHER_SECRET") is None


def test_tortoise_has_proper_source_metadata(settings):
    write(settings, {"SECRET": "tortoise_works_perfectly"})
    load(settings)
    history = get_history(
        settings,
        filter_callable=lambda s: s.loader == "tortoise",
    )
    assert history[0]["env"] == "development"
    assert history[0]["value"]["SECRET"] == "tortoise_works_perfectly"
