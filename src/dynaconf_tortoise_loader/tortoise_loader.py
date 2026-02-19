from typing import Any

from dynaconf import Dynaconf
from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils import build_env_list, upperfy
from dynaconf.utils.parse_conf import parse_conf_data, unparse_conf_data

from dynaconf_tortoise_loader.models import DynaconfStorage

try:
    from tortoise import Tortoise, run_async
except ImportError as _tie:
    raise ImportError(
        "Tortoise-ORM package is not installed in your environment. "
        "`pip install tortoise-orm` or disable the tortoise loader with "
        "export TORTOISE_ENABLED_FOR_DYNACONF=false",
    ) from _tie

IDENTIFIER = "tortoise"


async def _init_tortoise(obj: Dynaconf) -> None:
    db_url = obj.get("TORTOISE_URL_FOR_DYNACONF")
    if not db_url:
        raise ValueError("TORTOISE_URL_FOR_DYNACONF is required")

    config = {
        "connections": {"default": db_url},
        "apps": {
            "dynaconf_tortoise_loader": {
                "models": ["dynaconf_tortoise_loader.models"],
                "default_connection": "default",
            },
        },
    }
    await Tortoise.init(config)
    await Tortoise.generate_schemas(safe=True)


async def _load_data(holder: str, key: str | None = None) -> dict[str, Any]:
    if key:
        record = await DynaconfStorage.get_or_none(
            holder=holder.upper(),
            key=upperfy(key),
        )
        if record:
            return {key: record.value}
        return {}
    else:
        records = await DynaconfStorage.filter(holder=holder).all()
        return {record.key: record.value for record in records}


async def _save_data(holder: str, data: dict[str, Any]) -> None:
    for key, value in data.items():
        await DynaconfStorage.update_or_create(
            holder=holder.upper(),
            key=upperfy(key),
            defaults={"value": value},
        )


async def _delete_data(holder: str, key: str | None = None) -> None:
    if key:
        await DynaconfStorage.filter(
            holder=holder.upper(),
            key=upperfy(key),
        ).delete()
    else:
        await DynaconfStorage.filter(holder=holder.upper()).delete()


def load(
    obj: Dynaconf,
    env: str | None = None,
    silent: bool = True,
    key: str | None = None,
    validate: bool = False,
) -> None:
    prefix = obj.get("ENVVAR_PREFIX_FOR_DYNACONF")
    env_name = env or obj.current_env
    env_list = build_env_list(obj, env_name)

    if prefix and prefix not in env_list:
        env_list.insert(0, prefix)

    async def _inner() -> None:
        await _init_tortoise(obj)
        try:
            all_data = {}

            for search_env in env_list:
                if prefix:
                    if search_env == prefix:
                        holder = f"{prefix.upper()}"
                    else:
                        holder = f"{prefix.upper()}_{search_env.upper()}"
                else:
                    holder = search_env.upper()

                raw_data = await _load_data(holder, key=key)
                if raw_data:
                    parsed_data = {
                        k: parse_conf_data(v, tomlfy=True, box_settings=obj)
                        for k, v in raw_data.items()
                    }
                    all_data.update(parsed_data)

                    if key and key in parsed_data:
                        break

            if all_data:
                source_metadata = SourceMetadata(
                    IDENTIFIER,
                    "unique",
                    env_name.lower(),
                )

                if key:
                    if key in all_data:
                        obj.set(
                            key,
                            all_data[key],
                            validate=validate,
                            loader_identifier=source_metadata,
                        )
                else:
                    obj.update(
                        all_data,
                        loader_identifier=source_metadata,
                        validate=validate,
                    )
        finally:
            await Tortoise.close_connections()

    try:
        run_async(_inner())
        return
    except Exception as e:
        if not silent:
            raise e
        return


def write(
    obj: Dynaconf,
    data: dict[str, Any] | None = None,
    **kwargs: Any,
) -> None:
    if obj.TORTOISE_ENABLED_FOR_DYNACONF is False:
        raise RuntimeError(
            "Tortoise-ORM is not configured \n"
            "export TORTOISE_ENABLED_FOR_DYNACONF=true\n"
            "and configure the TORTOISE_*_FOR_DYNACONF variables",
        )

    holder = obj.get("ENVVAR_PREFIX_FOR_DYNACONF").upper()
    holder = f"{holder}_{obj.current_env.upper()}"

    data = data or {}
    data.update(kwargs)
    if not data:
        raise AttributeError("Data must be provided")

    tortoise_data = {}
    for key, value in data.items():
        upper_key = upperfy(key)
        unparsed_value = unparse_conf_data(value)
        tortoise_data[upper_key] = unparsed_value

    async def _inner() -> None:
        await _init_tortoise(obj)
        try:
            await _save_data(holder, tortoise_data)
        finally:
            await Tortoise.close_connections()

    try:
        run_async(_inner())
        load(obj)
        return
    except Exception as e:
        raise e


def delete(obj: Dynaconf, key: str | None = None) -> None:
    if obj.TORTOISE_ENABLED_FOR_DYNACONF is False:
        raise RuntimeError("Tortoise loader is disabled")

    holder = obj.get("ENVVAR_PREFIX_FOR_DYNACONF").upper()
    holder = f"{holder}_{obj.current_env.upper()}"

    async def _inner() -> None:
        await _init_tortoise(obj)
        try:
            await _delete_data(holder, key=key)
        finally:
            await Tortoise.close_connections()

    try:
        run_async(_inner())
        if key:
            obj.unset(key)
        return
    except Exception as e:
        raise e
