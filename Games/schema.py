from ninja import Schema

class Games(Schema):
    id: int
    name: str
    image: str
    fee: float
    winning_amount: float

class GameListOut(Schema):
    game: Games
    total_players: int