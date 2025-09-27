from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from Matches.models import *

game_api = Router(tags=["Game"])

################################################ Games ################################################
@game_api.get("/", response={200: List[GameListOut]})
async def get_games(request):
    games = [game async for game in Game.objects.filter(is_active=True).values("id", "name", "image", "fee", "winning_amount")]
    game_list = []
    for i in games:
        total_players = await Matches.objects.filter(game__id=i.get('id'), status='full').acount()
        game_list.append({
            "game": i,
            "total_players": total_players
        })
    return 200, game_list