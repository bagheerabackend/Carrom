from ninja import Schema

class TransactionIn(Schema):
    amount: int

class BalanceReponse(Schema):
    total_balance: int
    withdrawal_amount: int
    player_withdrawal: int