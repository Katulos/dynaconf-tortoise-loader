from typing import Any

from dynaconf import Dynaconf
from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils import upperfy
from dynaconf.utils.parse_conf import parse_conf_data, unparse_conf_data
from tortoise import Tortoise, run_async

from dynaconf_tortoise_loader.models import DynaconfStorage

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
    await Tortoise.generate_schemas()


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
        records = await DynaconfStorage.filter(holder=holder.upper()).all()
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
) -> bool:
    prefix = obj.get("ENVVAR_PREFIX_FOR_DYNACONF", "DYNACONF")
    env_name = env or obj.current_env
    holder = f"{prefix.upper()}_{env_name.upper()}"

    async def _inner() -> None:
        await _init_tortoise(obj)
        try:
            raw_data = await _load_data(holder, key=key)
            if not raw_data:
                return

            parsed_data = {
                k: parse_conf_data(v, tomlfy=True, box_settings=obj)
                for k, v in raw_data.items()
            }

            source_metadata = SourceMetadata(IDENTIFIER, "unique", env_name)

            if key:
                if key in parsed_data:
                    obj.set(
                        key,
                        parsed_data[key],
                        validate=validate,
                        loader_identifier=source_metadata,
                    )
            else:
                if parsed_data:
                    obj.update(
                        parsed_data,
                        loader_identifier=source_metadata,
                        validate=validate,
                    )
        finally:
            await Tortoise.close_connections()

    try:
        run_async(_inner())
        return True
    except Exception as e:
        if not silent:
            raise e
        return False


def write(
    obj: Dynaconf,
    data: dict[str, Any] | None = None,
    **kwargs: Any,
) -> bool:
    if obj.TORTOISE_ENABLED_FOR_DYNACONF is False:
        raise RuntimeError("Tortoise loader is disabled")

    data = data or {}
    data.update(kwargs)
    if not data:
        raise AttributeError("Data must be provided")

    prefix = obj.get("ENVVAR_PREFIX_FOR_DYNACONF", "DYNACONF")
    holder = f"{prefix.upper()}_{obj.current_env.upper()}"

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
        return True
    except Exception as e:
        raise e


def delete(obj: Dynaconf, key: str | None = None) -> bool:
    if obj.TORTOISE_ENABLED_FOR_DYNACONF is False:
        raise RuntimeError("Tortoise loader is disabled")

    prefix = obj.get("ENVVAR_PREFIX_FOR_DYNACONF", "DYNACONF")
    holder = f"{prefix.upper()}_{obj.current_env.upper()}"

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
        return True
    except Exception as e:
        raise e
