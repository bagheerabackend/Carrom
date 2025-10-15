from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from Player.schema import Message
from Player.models import Player
from .signals import player_disconnected_signal
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.core.cache import cache

match_api = Router(tags=["Matches"])

################################################ Match Making ################################################
@match_api.post("/match-making", response={201: MatchStartingOut, 206: MatchMakingOut, 404: Message, 402: Message, 409: Message, 405: Message})
async def match_making(request, data: MatchMakingIn):
    if await Game.objects.filter(id=data.game_id).aexists():
        user = request.auth
        if user.is_blocked:
            return 409, {"message": "Player blocked"}
        
        game = await Game.objects.aget(id=data.game_id)
        entry_amount = user.bonus if game.type == "bonus" else (user.coin + user.cashback)

        if (entry_amount) >= game.fee:
            if await Matches.objects.filter(game=game, status="waiting").aexists():
                match = await Matches.objects.filter(game=game, status="waiting").afirst()
                player1 = await sync_to_async(lambda: match.player1)()
                if player1 == user and await sync_to_async(lambda: match.player2)() is None:
                    player1_id = await sync_to_async(lambda: match.player1.player_id)()
                    return 206, {
                        "match_id": match.id,
                        "player1_id": player1_id,
                        "player1_name": match.player1.name,
                        "player1_avatar_no": match.player1.avatar_no
                    }
                match.player2 = user
                match.status = "full"
                match.winning_amount = game.winning_amount
                game_fee = await sync_to_async(lambda: match.game.fee)()
                match.commission_amount = (game_fee * 2) - game.winning_amount
                await match.asave()
                if game.type == "bonus":
                    user.bonus -= game.fee
                else:
                    if user.cashback >= game.fee:
                        user.cashback -= game.fee
                    else:
                        if user.cashback > 0:
                            money = user.cashback
                            user.cashback = 0
                            user.coin -= (game.fee - money)
                        else:
                            user.coin -= game.fee
                await sync_to_async(cache.delete)(f"coins_{user.player_id}")
                await user.asave()
                player2_id = await sync_to_async(lambda: match.player2.player_id)()
                return 201, {
                    "match_id": match.id,
                    "player1_id": player1_id,
                    "player1_name": match.player1.name,
                    "player1_avatar_no": match.player1.avatar_no,
                    "player2_id": player2_id,
                    "player2_name": match.player2.name,
                    "player2_avatar_no": match.player2.avatar_no,
                    "winning_amount": match.winning_amount
                }
            q = Q(game=game, status="full")
            q &= (Q(player1=user) | Q(player2=user))
            if await Matches.objects.filter(q).aexists():
                match = await Matches.objects.filter(q).afirst()
                player1_id = await sync_to_async(lambda: match.player1.player_id)()
                player2_id = await sync_to_async(lambda: match.player2.player_id)()
                return 201, {
                    "match_id": match.id,
                    "player1_id": player1_id,
                    "player1_name": match.player1.name,
                    "player1_avatar_no": match.player1.avatar_no,
                    "player2_id": player2_id,
                    "player2_name": match.player2.name,
                    "player2_avatar_no": match.player2.avatar_no,
                    "winning_amount": match.winning_amount
                }
            if game.type == "bonus":
                user.bonus -= game.fee
            else:
                if user.cashback >= game.fee:
                    user.cashback -= game.fee
                else:
                    if user.cashback > 0:
                        money = user.cashback
                        user.cashback = 0
                        user.coin -= (game.fee - money)
                    else:
                        user.coin -= game.fee
            await sync_to_async(cache.delete)(f"coins_{user.player_id}")
            await user.asave()
            match = Matches(game=game, player1=user)
            await match.asave()
            return 206, {
                "match_id": match.id,
                "player1_id": match.player1.id,
                "player1_name": match.player1.name,
                "player1_avatar_no": match.player1.avatar_no
            }
        return 402, {"message": "Insufficient coins"}
    return 404, {"message": "Game does not exist"}

@match_api.get("/cancel-match", response={200: Message, 404: Message, 409: Message})
async def cancel_match(request, match_id: int):
    user = request.auth
    if await Matches.objects.filter(id=match_id, player1=user, status="waiting").aexists():
        match = await Matches.objects.aget(id=match_id)
        game = await sync_to_async(lambda: match.game)()
        if game.type == "bonus":
            user.bonus += game.fee
        else:
            if user.cashback >= 0:
                user.cashback += game.fee
            else:
                user.coin += game.fee
        await sync_to_async(cache.delete)(f"coins_{user.player_id}")
        await user.asave()
        await match.adelete()
        if user.is_blocked:
            return 409, {"message": "Player blocked"}
        return 200, {"message": "Match cancelled successfully"}
    return 404, {"message": "Match does not exist or cannot be cancelled"}

################################################ Match Connection ################################################
@match_api.patch("/player-disconnected", response={200: Message, 404: Message})
async def player_disconnected(request, match_id: int, player_id: str):
    if await Matches.objects.filter(id=match_id).aexists():
        match = await Matches.objects.aget(id=match_id)
        if match.status != "completed":
            player1_id = await sync_to_async(lambda: match.player1.player_id)()
            player2_id = await sync_to_async(lambda: match.player2.player_id)()
            if player1_id == player_id:
                match.player1_disconnected = True
            elif player2_id == player_id:
                match.player2_disconnected = True
            else:
                return 404, {"message": "Player not part of this match"}
            await match.asave()
            player_disconnected_signal.send(
                sender=None,
                match_id=match_id,
                player_id=player_id
            )
            return 200, {"message": "Player disconnection status updated"}
        return 404, {"message": "Match already completed"}
    
@match_api.patch("/player-reconnected", response={200: Message, 404: Message})
async def player_reconnected(request, match_id: int, player_id: int):
    if await Matches.objects.filter(id=match_id).aexists():
        match = await Matches.objects.aget(id=match_id)
        if match.status != "completed":
            if match.player1.player_id == player_id:
                match.player1_disconnected = False
            elif match.player2.player_id == player_id:
                match.player2_disconnected = False
            else:
                return 404, {"message": "Player not part of this match"}
            await match.asave()
            return 200, {"message": "Player reconnection status updated"}
        return 404, {"message": "Match already completed"}
    return 404, {"message": "Match does not exist"}

################################################ Match Result ################################################
@match_api.patch("/match-result", response={200: MatchResultOut, 404: Message})
async def match_result(request, data: MatchResultIn):
    if await Matches.objects.filter(id=data.match_id).aexists():
        match = await Matches.objects.aget(id=data.match_id)
        player1_id = await sync_to_async(lambda: match.player1.player_id)()
        player2_id = await sync_to_async(lambda: match.player2.player_id)()
        game_type = await sync_to_async(lambda: match.game.type)()
        if not match.status == "completed":
            if player1_id == data.winner_id or player2_id == data.winner_id:
                winner = await Player.objects.aget(player_id=data.winner_id)
                if game_type == "bonus":
                    winner.bonus += match.winning_amount
                else:
                    winner.withdrawable_coin += (match.winning_amount - match.game.fee)
                    winner.coin += match.winning_amount
                await sync_to_async(cache.delete)(f"coins_{winner.player_id}")
                await winner.asave()
                match.winner = winner
                winner_id = await sync_to_async(lambda: winner.player_id)()
                match.status = "completed"
                await match.asave()
                return 200, {
                    "match_id": match.id,
                    "player1_id": player1_id,
                    "player1_name": match.player1.name,
                    "player1_avatar_no": match.player1.avatar_no,
                    "player2_id": player2_id,
                    "player2_name": match.player2.name,
                    "player2_avatar_no": match.player2.avatar_no,
                    "winner_id": winner_id,
                    "winning_amount": match.winning_amount
                }
            return 200, {"message": "Winner must be either player1 or player2"}
        return 200, {
            "match_id": match.id,
            "player1_id": player1_id,
            "player1_name": match.player1.name,
            "player1_avatar_no": match.player1.avatar_no,
            "player2_id": player2_id,
            "player2_name": match.player2.name,
            "player2_avatar_no": match.player2.avatar_no,
            "winner_id": await sync_to_async(lambda: match.winner.player_id)(),
            "winning_amount": match.winning_amount
        }
    return 404, {"message": "Match does not exist"}

################################################ Bonus Update ################################################
@match_api.patch("/update-bonus", response={200: Message, 404: Message, 405: Message, 409: Message})
async def update_bonus(request, bonus: float):
    user = request.auth
    if user.is_blocked:
        return 409, {"message": "Player blocked"}
    if user.bonus != 0:
        if bonus > 0:
            user.bonus -= bonus
            await sync_to_async(cache.delete)(f"coins_{user.player_id}")
            await user.asave()
            return 200, {"message": "Bonus updated successfully"}
        return 404, {"message": "Invalid bonus amount"}
    return 405, {"message": "No bonus to update"}