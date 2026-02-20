# Dynaconf Tortoise ORM Loader

![PyPI - License](https://img.shields.io/pypi/l/dynaconf-tortoise-loader?logo=pypi)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/dynaconf-tortoise-loader?logo=pypi)
![PyPI - Version](https://img.shields.io/pypi/v/dynaconf-tortoise-loader?logo=pypi)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dynaconf-tortoise-loader?logo=pypi)

![release](https://github.com/Katulos/dynaconf-tortoise-loader/actions/workflows/release.yml/badge.svg)
![develop](https://github.com/Katulos/dynaconf-tortoise-loader/actions/workflows/develop.yml/badge.svg?branch=develop)

Implementing Dynaconf settings storage in a database using the Tortoise ORM framework.


## Installation

`pip install dynaconf-tortoise-loader`

By default, Tortoise ORM comes with a sqlite database driver.

If you require a different database driver, please refer to the [Tortoise ORM documentation](https://tortoise.github.io/getting_started.html#installation).

## Usage

1. Create a `config.py` file in your project

    ```python
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
    ```

    The `TORTOISE_URL_FOR_DYNACONF`value must contain the database connection string. See the [Tortoise ORM documentation](https://tortoise.github.io/databases.html#db-url) for more details.

    `TORTOISE_URL_FOR_DYNACONF` does not need to be declared directly in the code, but can be declared in the settings files listed in `settings_files` or set via an environment variable.

    For more information, please refer to the [Dynaconf documentation](https://www.dynaconf.com/configuration/).

2. Use the `settings` object in your code
   
    ```python
    form .config import settings

    # set and store settings
    settings.host = "localhost"
    settings.port = 8022

    # get settings
    print(settings.get("host"))
    print(settings.get("port"))
    ```
    
    See [more example](examples/sqlite)

