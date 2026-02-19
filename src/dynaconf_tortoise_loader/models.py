import logging

from tortoise import BaseDBAsyncClient, fields
from tortoise.models import Model
from tortoise.signals import post_save

_logger = logging.getLogger("dynaconf")


class DynaconfStorage(Model):
    id = fields.BigIntField(primary_key=True)
    holder = fields.CharField(max_length=255, db_index=True)
    key = fields.CharField(max_length=255, db_index=True)
    value = fields.TextField(null=True)

    class Meta:
        table = "dynaconf_storage"
        unique_together = (("holder", "key"),)


@post_save(DynaconfStorage)
async def dynaconf_storage_post_save(
    sender: type[DynaconfStorage],
    instance: DynaconfStorage,
    created: bool,
    using_db: BaseDBAsyncClient | None,
    update_fields: list[str],
) -> None:
    # pylint: disable=unused-argument
    _logger.debug(
        "Config parameter saved: %s: %s",
        instance.key,
        instance.value,
    )
