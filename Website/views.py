from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from Player.schema import Message
from django.db.models import Q

web_api = Router(tags=["Web"])

################################################ Games ################################################
@web_api.get("/games", auth=None, response={200: List[WebGameSchema]})
async def get_games(request):
    q = Q(is_active=True)
    games = []
    async for game in WebGames.objects.filter(q):
        games.append({
            "id": game.id,
            "name": game.name,
            "description": game.description,
            "bg_image": game.bg_image.url if game.bg_image else '',
            "game_image": game.game_image.url if game.game_image else '',
            "live": game.live,
            "playstore_url": game.playstore_url,
            "appstore_url": game.appstore_url,
        })
    return 200, games

@web_api.post("/contact-us", auth=None, response={201: Message})
async def create_contact(request, data: ContactSchema):
    contact = ContactUsWeb(**data.dict())
    await contact.asave()
    return 201, {"message": "Message send succesfully!"}
