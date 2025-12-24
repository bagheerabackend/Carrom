from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from Player.schema import Message
from Player.models import Player
from asgiref.sync import sync_to_async
from django.core.cache import cache

settings_api = Router(tags=["Settings"])

################################################ App Settings ################################################
@settings_api.get("/app-settings", auth=None, response={200: Settings, 404: Message})
async def app_settings(request):
    cache_key = "app_settings"
    cached_settings = await sync_to_async(cache.get)(cache_key)
    if cached_settings:
        return 200, cached_settings
    if await AppSettings.objects.aexists():
        settings = await AppSettings.objects.alast()
        settings_data = {
            "maintenance_mode": settings.maintenance_mode,
            "maintenance_message": settings.maintenance_message,
            "app_version": settings.version,
            "force_update": settings.force_update,
        }
        await sync_to_async(cache.set)(cache_key, settings_data, 3600)
        return 200, settings_data
    return 404, {"message": "Settings not found"}