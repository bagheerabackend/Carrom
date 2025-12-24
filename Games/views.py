from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from Matches.models import *
from django.db.models import Q
from django.core.cache import cache
from asgiref.sync import sync_to_async
from django.db.models import Count

game_api = Router(tags=["Game"])

################################################ Games ################################################
@game_api.get("/", response={200: List[GameListOut]})
async def get_games(request, type: str):
    cache_key = f"games_list_{type}"
    cached_games = await sync_to_async(cache.get)(cache_key)
    if cached_games:
        return 200, cached_games
    q = Q(is_active=True)
    if type:
        q &= Q(type=type)
    games = [game async for game in Game.objects.filter(q).values("id", "name", "image", "fee", "winning_amount").annotate(full_matches=Count('matches', filter=Q(matches__status='full')), waiting_matches=Count('matches', filter=Q(matches__status='waiting')))]
    game_list = [{
        "game": {
            "id": game["id"],
            "name": game["name"],
            "image": game["image"],
            "fee": game["fee"],
            "winning_amount": game["winning_amount"],
        },
        "total_players": (game["full_matches"] * 2) + game["waiting_matches"]
    } for game in games]
    await sync_to_async(cache.set)(cache_key, game_list, 120)
    return 200, game_list