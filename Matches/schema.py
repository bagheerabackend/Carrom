from ninja import Schema
from typing import Optional

class MatchMakingIn(Schema):
    game_id: int

class MatchMakingOut(Schema):
    match_id: int
    player1_id: int
    player1_name: str
    player1_avatar_no: int

class MatchStartingOut(Schema):
    match_id: int
    player1_id: str
    player1_name: str
    player1_avatar_no: int
    player2_id: str
    player2_name: str
    player2_avatar_no: int
    winning_amount: float

class MatchResultIn(Schema):
    match_id: int
    winner_id: Optional[str] = None

class MatchResultOut(Schema):
    match_id: int
    player1_id: str
    player1_name: str
    player1_avatar_no: int
    player2_id: str
    player2_name: str
    player2_avatar_no: int
    winner_id: str
    winning_amount: float