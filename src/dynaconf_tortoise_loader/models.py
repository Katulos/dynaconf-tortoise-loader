import logging

from tortoise import BaseDBAsyncClient, fields
from tortoise.models import Model
from tortoise.signals import post_save

_logger = logging.getLogger("dynaconf")


class DynaconfStorage(Model):
    id = fields.BigIntField(pk=True)
    key = fields.CharField(max_length=255)
    value = fields.TextField()

    class Meta:
        table = "dynaconf_storage"


@post_save(DynaconfStorage)
async def dynaconf_storage_post_save(
    sender: type[DynaconfStorage],
    instance: DynaconfStorage,
    created: bool,
    using_db: BaseDBAsyncClient | None,
    update_fields: list[str],
) -> None:
    # pylint: disable=unused-argument
    _logger.info(
        "Config parameter saved: %s: %s",
        instance.key,
        instance.value,
    )
