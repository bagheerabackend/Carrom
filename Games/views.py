from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *

game_api = Router(tags=["Game"])

################################################ Games ################################################
@game_api.get("/", response={200: List[GameOut]})
async def get_games(request):
    games = [game async for game in Game.objects.all().values("id", "name", "image", "fee", "winning_amount")]
    return 200, list(games)