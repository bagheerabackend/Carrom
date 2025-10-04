from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from Player.schema import Message
from django.db.models import Q

web_api = Router(tags=["Web"])

################################################ Games ################################################
@web_api.get("/games", response={200: List[WebGameSchema]})
async def get_games(request):
    q = Q(is_active=True)
    games = [game async for game in WebGames.objects.filter(q).values("id", "name",  "description", "bg_image", "game_image", "live", "playstore_url", "appstore_url")]
    return 200, games

@web_api.post("/contact-us", response={201: Message})
async def create_contact(request, data: ContactSchema):
    contact = ContactUsWeb(**data.dict())
    contact.asave()
    return 201, {"message": "Message send succesfully!"}
