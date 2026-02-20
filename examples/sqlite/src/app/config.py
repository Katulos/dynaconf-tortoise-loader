import logging
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf, ValidationError
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils.functional import empty

from dynaconf_tortoise_loader import loader

_BASE_DIR = Path.cwd()
_DB_PATH = _BASE_DIR / "data" / "settings.sqlite3"


class Config(Dynaconf):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._initialized = True

    def __setattr__(self, name: str, value: Any) -> None:
        if name not in [
            "_wrapped",
            "_kwargs",
            "_warn_dynaconf_global_settings",
        ]:
            if self._wrapped is empty:
                self._setup()

        super().__setattr__(name, value)

        if hasattr(self, "_initialized") and self._initialized:
            try:
                data = DynaBox({name: value}, box_settings={}).to_dict()
                loader.write(self, data)
            except Exception as e:
                logging.error(e)


settings = Config(
    # Define the environments to use
    # environments=True,
    envvar_prefix="MYAPP",
    settings_files=[
        _BASE_DIR / "settings.toml",
        _BASE_DIR / ".secrets.toml",
    ],
    LOADERS_FOR_DYNACONF=[
        "dynaconf_tortoise_loader.loader",  # require custom loader
        "dynaconf.loaders.env_loader",  # require dotenv loader
    ],
    TORTOISE_ENABLED_FOR_DYNACONF=True,
    TORTOISE_URL_FOR_DYNACONF=f"sqlite://{_DB_PATH}",
)

try:
    settings.validators.validate_all()
except ValidationError as e:
    logging.error(e.message)
