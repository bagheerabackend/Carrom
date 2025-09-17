from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from Player.schema import Message
from Player.models import Player
from .signals import player_disconnected_signal
from asgiref.sync import sync_to_async

match_api = Router(tags=["Matches"])

################################################ Match Making ################################################
@match_api.post("/match-making", response={201: MatchStartingOut, 206: MatchMakingOut, 404: Message, 402: Message})
async def match_making(request, data: MatchMakingIn):
    if await Game.objects.filter(id=data.game_id).aexists():
        user = request.auth
        if user.coin >= game.entry_amount:
            game = await Game.objects.aget(id=data.game_id)
            user.coin -= game.entry_amount
            await user.asave()
            if await Matches.objects.filter(game=game, status="waiting").aexists():
                match = await Matches.objects.filter(game=game, status="waiting").afirst()
                match.player2 = user
                match.status = "full"
                match.winning_amount = game.winning_amount
                match.commission_amount = 0
                await match.asave()
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
            match = Matches(game=game, player1=user)
            await match.asave()
            return 206, {
                "player1_id": match.player1.id,
                "player1_name": match.player1.name,
                "player1_avatar_no": match.player1.avatar_no
            }
        return 402, {"message": "Insufficient coins"}
    return 404, {"message": "Game does not exist"}

@match_api.get("/cancel-match", response={200: Message, 404: Message})
async def cancel_match(request, match_id: int):
    user = request.auth
    if await Matches.objects.filter(id=match_id, player1=user, status="waiting").aexists():
        match = await Matches.objects.aget(id=match_id)
        await match.adelete()
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
        if not match.status == "completed":
            if player1_id == data.winner_id or player2_id == data.winner_id:
                winner = await Player.objects.aget(player_id=data.winner_id)
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
            return 404, {"message": "Winner must be either player1 or player2"}
        print("Match already completed")
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
@match_api.patch("/update-bonus", response={200: Message, 404: Message})
async def update_bonus(request, bonus: float):
    user = request.auth
    if bonus > 0:
        user.bonus += bonus
        await user.asave()
        return 200, {"message": "Bonus updated successfully"}
    return 404, {"message": "Invalid bonus amount"}