from ninja import Schema

class GameOut(Schema):
    id: int
    name: str
    image: str
    fee: float
    winning_amount: float