from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from Matches.models import *
from django.db.models import Q
from django.core.cache import cache

game_api = Router(tags=["Game"])

################################################ Games ################################################
@game_api.get("/", response={200: List[GameListOut]})
async def get_games(request, type):
    cache_key = f"games_list_{type}" if type else "games_list_all"
    cached_games = cache.get(cache_key)
    if cached_games:
        return 200, cached_games
    q = Q(is_active=True)
    if type:
        q &= Q(type=type)
    games = [game async for game in Game.objects.filter(q).values("id", "name", "image", "fee", "winning_amount")]
    game_list = []
    for i in games:
        total_players = await Matches.objects.filter(game__id=i.get('id'), status='full').acount()
        game_list.append({
            "game": i,
            "total_players": total_players
        })
    cache.set(cache_key, game_list, 120)
    return 200, game_list