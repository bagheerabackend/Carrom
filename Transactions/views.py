from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from django.utils import timezone
from Player.schema import Message
from Settings.models import AppSettings

transaction_api = Router(tags=["Transaction"])

################################################ Debit and Credit ################################################
@transaction_api.post("/credit-transaction", response={200: Message, 404: Message, 405: Message, 409: Message})
async def credit_transaction(request, data: TransactionIn):
    user = request.auth
    if user.is_blocked:
        return 409, {"message": "Player blocked"}
    if data.amount > 0:

        ########### GST Calculation ###########
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

@transaction_api.post("/debit-transaction", response={200: Message, 403: Message, 404: Message, 405: Message, 406: Message, 409: Message})
async def debit_transaction(request, data: TransactionIn):
    user = request.auth
    if user.is_blocked:
        return 409, {"message": "Player blocked"}
    if data.amount <= 0:
        return 405, {"message": "Amount must be greater than zero"}

    settings = await AppSettings.objects.alast()
    today = timezone.now()
    # if not await TransactionLog.objects.filter(user=user, transaction_at__date=today).acount() < settings.daily_withdraw_count:
    #     return 403, {"message": "Daily Transaction Limit Completed"}
    # if data.amount < settings.withdrawal_limit:
    #     return 406, {"message": f"Minimum amount of {settings.withdrawal_limit} required for withdrawal"}

    # if user.pan_no:
    if user.withdrawable_coin >= data.amount:

        ########### TDS Calculation ###########
        ########### Razorpay Integration ###########

        user.coin -= data.amount
        user.withdrawable_coin -= data.amount
        await user.asave()
        tds_percentage = settings.tds_percentage / 100
        gst_deduct = data.amount - (data.amount * tds_percentage)
        transaction = TransactionLog(
            user=user,
            amount=data.amount,
            gst_deduct=gst_deduct,
            balance_after=user.coin,
            transaction_type='debit'
        )
        await transaction.asave()
        return 200, {"message": "Transaction successful"}
    return 405, {"message": "Insufficient balance"}
    # return 404, {"message": "Aadhar not verified"}

@transaction_api.get("/balance-check", response={200: BalanceReponse, 404: Message, 409: Message})
async def balance_check(request):
    user = request.auth
    if user.is_blocked:
        return 409, {"message": "Player blocked"}
    withdrawal_amount = user.withdrawable_coin
    settings = await AppSettings.objects.alast()
    tds_percentage = settings.tds_percentage / 100
    player_withdrawal = withdrawal_amount - (withdrawal_amount * tds_percentage)
    return 200, {
        "total_balance": user.coin,
        "withdrawal_amount": withdrawal_amount,
        "player_withdrawal": player_withdrawal,
    }
    return 404, {"message": "Insufficient balance"}