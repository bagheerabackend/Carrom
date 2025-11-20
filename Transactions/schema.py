from ninja import Schema
from typing import *

class TransactionIn(Schema):
    amount: int
    order_id: Optional[str] = None
    status: Optional[str] = 'pending'

class BalanceReponse(Schema):
    total_balance: int
    withdrawal_amount: int
    player_withdrawal: int

class TransactionHistory(Schema):
    transaction_id: int
    amount: int
    order_id: str
    status: str