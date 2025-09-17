from ninja import Schema
from typing import *

class Message(Schema):
    message: str

class OtpIn(Schema):
    email: str

class OtpVerify(Schema):
    name: str
    age: int
    phone: str
    password: str
    email: str
    otp: int

class LoginIn(Schema):
    username: str
    password: str

class TokenOut(Schema):
    access: str
    refresh: str

class RefreshTokenIn(Schema):
    refresh: str

class ChangePasswordIn(Schema):
    password: str

class BonusOut(Schema):
    bonus: float
    coin: int

class PlayerOut(Schema):
    player_id: str
    name: str
    avatar_no: int
    # total_games: int
    # total_wons: int
    # total_loss: int