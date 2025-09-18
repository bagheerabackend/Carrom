from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from Player.schema import Message

transaction_api = Router(tags=["Transaction"])

################################################ Debit and Credit ################################################
@transaction_api.post("/credit-transaction", response={200: Message, 404: Message, 405: Message})
async def credit_transaction(request, data: TransactionIn):
    user = request.auth
    if data.amount > 0:

        ########### Razorpay Integration ###########

        user.coin += data.amount
        await user.asave()
        transaction = TransactionLog(
            user=user,
            amount=data.amount,
            gst_deduct=0.0,
            balance_after=user.coin,
            transaction_type='credit'
        )
        await transaction.asave()
        return 200, {"message": "Transaction successful"}
    return 405, {"message": "Amount must be greater than zero"}

@transaction_api.post("/debit-transaction", response={200: Message, 404: Message, 405: Message})
async def debit_transaction(request, data: TransactionIn):
    user = request.auth
    if data.amount > 0:
        return 405, {"message": "Amount must be greater than zero"}
    if user.aadhar_verified:
        if user.coin >= data.amount:

            ########### Razorpay Integration ###########

            user.coin -= data.amount
            await user.asave()
            transaction = TransactionLog(
                user=user,
                amount=data.amount,
                gst_deduct=0.0,
                balance_after=user.coin,
                transaction_type='debit'
            )
            await transaction.asave()
            return 200, {"message": "Transaction successful"}
        return 405, {"message": "Insufficient balance"}
    return 404, {"message": "Aadhar not verified"}

@transaction_api.get("/balance-check", response={200: Message, 404: Message})
async def balance_check(request, coin: int):
    user = request.auth
    if user.coin >= coin:
        return 200, {"message": "Sufficient balance"}
    return 404, {"message": "Insufficient balance"}