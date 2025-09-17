from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from Player.schema import Message
from Player.models import Player
from asgiref.sync import sync_to_async

settings_api = Router(tags=["Settings"])

################################################ App Settings ################################################
@settings_api.get("/app-settings", auth=None, response={200: Settings, 404: Message})
async def app_settings(request):
    if await AppSettings.objects.aexists():
        settings = await AppSettings.objects.afirst()
        return 200, {
            "maintenance_mode": settings.maintenance_mode,
            "maintenance_message": settings.maintenance_message,
            "app_version": settings.version
        }
    return 404, {"message": "Settings not found"}