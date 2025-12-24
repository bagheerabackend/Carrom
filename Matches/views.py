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

        if await Matches.objects.filter(game=game, status="waiting").aexists():
            match = await Matches.objects.filter(game=game, status="waiting").afirst()
            player1 = await sync_to_async(lambda: match.player1)()
            player2 = await sync_to_async(lambda: match.player2)()
            if player1 == user and player2 is None:
                player1_id = await sync_to_async(lambda: match.player1.player_id)()
                return 206, {
                    "match_id": match.id,
                    "player1_id": player1_id,
                    "player1_name": match.player1.name,
                    "player1_avatar_no": match.player1.avatar_no,
                    "winning_amount": match.winning_amount
                }
            if (entry_amount) >= game.fee:
                match.player2 = user
                match.status = "full"
                game_fee = await sync_to_async(lambda: match.game.fee)()
                match.commission_amount = (game_fee * 2) - game.winning_amount
                await match.asave()
                cashback_used = 0
                if game.type == "bonus":
                    user.bonus -= game.fee
                else:
                    if user.cashback >= game.fee:
                        user.cashback -= game.fee
                        cashback_used = game.fee
                        user.coin -= game.fee
                    else:
                        if user.cashback > 0:
                            cashback_used = user.cashback
                            user.cashback = 0
                            user.coin -= game.fee
                            user.withdrawable_coin -= (game.fee - cashback_used)
                        else:
                            user.coin -= game.fee
                            user.withdrawable_coin -= game.fee
                await sync_to_async(cache.delete)(f"player_profile_{user.player_id}")
                await sync_to_async(cache.delete)(f"coins_{user.player_id}")
                await sync_to_async(cache.delete)(f'games_list_{game.type}')
                user.cashback_used = cashback_used
                await user.asave()
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
            return 402, {"message": "Insufficient coins"}
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
        if (entry_amount) >= game.fee:
            cashback_used = 0
            if game.type == "bonus":
                user.bonus -= game.fee
            else:
                if user.cashback >= game.fee:
                    user.cashback -= game.fee
                    cashback_used = game.fee
                    user.coin -= game.fee
                else:
                    if user.cashback > 0:
                        cashback_used = user.cashback
                        user.cashback = 0
                        user.coin -= game.fee
                        user.withdrawable_coin -= (game.fee - cashback_used)
                    else:
                        user.coin -= game.fee
                        user.withdrawable_coin -= game.fee
            await sync_to_async(cache.delete)(f"player_profile_{user.player_id}")
            await sync_to_async(cache.delete)(f"coins_{user.player_id}")
            await sync_to_async(cache.delete)(f'games_list_{game.type}')
            user.cashback_used = cashback_used
            await user.asave()
            match = Matches(game=game, player1=user, winning_amount=game.winning_amount)
            await match.asave()
            return 206, {
                "match_id": match.id,
                "player1_id": match.player1.player_id,
                "player1_name": match.player1.name,
                "player1_avatar_no": match.player1.avatar_no,
                "winning_amount": match.winning_amount
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
            cashback_used = user.cashback_used
            user.cashback += cashback_used
            user.coin += (game.fee)
            user.withdrawable_coin += (game.fee - cashback_used)
            user.cashback_used = 0
        await sync_to_async(cache.delete)(f"coins_{user.player_id}")
        await user.asave()
        await match.adelete()
        if user.is_blocked:
            return 409, {"message": "Player blocked"}
        return 200, {"message": "Match cancelled successfully"}
    return 404, {"message": "Match does not exist or cannot be cancelled"}

@match_api.get("/delete-match", response={200: Message, 404: Message, 409: Message})
async def delete_match(request, match_id: int):
    user = request.auth
    if await Matches.objects.filter(id=match_id).aexists():
        match = await Matches.objects.select_related('player1', 'player2', 'game').aget(id=match_id)
        player1 = match.player1
        player2 = match.player2
        game_fee = match.game.fee
        if match.game.type == "bonus":
            player1.bonus += game_fee
            player2.bonus += game_fee
        else:
            player1_cashback_used = player1.cashback_used
            player1.cashback += player1_cashback_used
            player1.coin += (game_fee)
            player1.withdrawable_coin += (game_fee - player1_cashback_used)
            player1.cashback_used = 0
            player2_cashback_used = player2.cashback_used
            player2.cashback += player2_cashback_used
            player2.coin += (game_fee)
            player2.withdrawable_coin += (game_fee - player2_cashback_used)
            player2.cashback_used = 0
        await player1.asave()
        await player2.asave()
        await sync_to_async(cache.delete)(f"coins_{player1.player_id}")
        await sync_to_async(cache.delete)(f"coins_{player2.player_id}")
        await match.adelete()
        if user.is_blocked:
            return 409, {"message": "Player blocked"}
        return 200, {"message": "Match deleted successfully"}
    return 404, {"message": "Match does not exist"}

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
        match = await Matches.objects.select_related('player1', 'player2', 'game').aget(id=data.match_id)
        player1_id = await sync_to_async(lambda: match.player1.player_id)()
        player2_id = await sync_to_async(lambda: match.player2.player_id)()
        game_type = await sync_to_async(lambda: match.game.type)()
        if not match.status == "completed":
            if player1_id == data.winner_id or player2_id == data.winner_id:
                winner = await Player.objects.aget(player_id=data.winner_id)
                if game_type == "bonus":
                    winner.bonus += match.winning_amount
                else:
                    winner.coin += match.winning_amount
                    winner.withdrawable_coin = winner.coin - winner.cashback
                    winner.cashback_used = 0
                await sync_to_async(cache.delete)(f"coins_{winner.player_id}")
                await winner.asave()
                if winner == match.player1:
                    match.player2.cashback_used = 0
                    await match.player2.asave()
                else:
                    match.player1.cashback_used = 0
                    await match.player1.asave()
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

################################################ Match History ################################################
@match_api.get("/match-history", response={200: List[MatchHistoryOut], 409: Message})
async def match_history(request):
    user = request.auth
    if user.is_blocked:
        return 409, {"message": "Player blocked"}
    matches_list = []
    async for match in Matches.objects.filter(Q(player1=user) | Q(player2=user)).select_related('game', 'winner').order_by('-id'):
        matches_list.append({
            'match_id': match.id,
            'game_name': match.game.name,
            'game_type': match.game.type,
            'fee': match.game.fee,
            'match_status': 'won' if match.winner == user else 'lose',
            'winning_amount': match.winning_amount
        })
    return 200, matches_list