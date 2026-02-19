import os
import tempfile
import uuid

import pytest
import pytest_asyncio
from dynaconf import LazySettings


@pytest_asyncio.fixture(scope="session")
async def db_url():
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"pytest.{uuid.uuid4().hex}.sqlite3")
    test_dsn = f"sqlite:///{temp_path}"
    try:
        yield test_dsn
    finally:
        pass
        # os.remove(temp_path)


@pytest.fixture
def settings(db_url):
    return LazySettings(
        environments=True,
        TORTOISE_ENABLED_FOR_DYNACONF=True,
        TORTOISE_URL_FOR_DYNACONF=db_url,
    )
