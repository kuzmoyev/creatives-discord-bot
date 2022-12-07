from asgiref.sync import sync_to_async
from django.db import models


class QuerySetWithAsync(models.query.QuerySet):
    async def get_async(self, *args, **kwargs):
        return await sync_to_async(super().get)(*args, **kwargs)

    async def get_or_create_async(self, *args, **kwargs):
        return await sync_to_async(super().get_or_create)(*args, **kwargs)

    async def update_or_create_async(self, *args, **kwargs):
        return await sync_to_async(super().update_or_create)(*args, **kwargs)

    async def filter_async(self, *args, **kwargs):
        return await sync_to_async(super().filter)(*args, **kwargs)

    async def values_list_async(self, *args, **kwargs):
        return await sync_to_async(super().values_list)(*args, **kwargs)

    async def all_async(self, *args, **kwargs):
        return await sync_to_async(super().all)(*args, **kwargs)

    async def create_async(self, *args, **kwargs):
        return await sync_to_async(super().create)(*args, **kwargs)

    async def count_async(self, *args, **kwargs):
        return await sync_to_async(super().count)(*args, **kwargs)


class ManagerWithAsync(models.Manager.from_queryset(QuerySetWithAsync)):
    pass


class AsyncModel(models.Model):
    objects = ManagerWithAsync()

    async def save_async(self, *args, **kwargs):
        return await sync_to_async(super().save)(*args, **kwargs)

    class Meta:
        abstract = True
