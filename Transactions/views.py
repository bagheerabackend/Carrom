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

        settings = await AppSettings.objects.alast()
        gst_deduct = 0
        if data.status == 'success':
            tds_percentage = settings.gst_percentage / 100
            gst_deduct = data.amount * tds_percentage
            balance_after = data.amount - gst_deduct
            user.coin += data.amount
            user.cashback += gst_deduct
            user.withdrawable_coin += balance_after
            await user.asave()
        transaction = TransactionLog(
            user=user,
            amount=data.amount,
            gst_deduct=gst_deduct,
            balance_after=user.coin,
            transaction_type='credit',
            order_id=data.order_id,
            status=data.status
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

        gst_deduct = 0
        if data.status == 'success':
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
            transaction_type='debit',
            order_id=data.order_id,
            status=data.status
        )
        await transaction.asave()
        return 200, {"message": "Transaction successful"}
    return 405, {"message": "Insufficient balance"}
    # return 404, {"message": "Aadhar not verified"}

@transaction_api.get("/balance-check", response={200: BalanceReponse, 404: BalanceReponse, 409: Message})
async def balance_check(request, coin: int):
    user = request.auth
    if user.is_blocked:
        return 409, {"message": "Player blocked"}
    withdrawal_amount = user.withdrawable_coin
    settings = await AppSettings.objects.alast()
    tds_percentage = settings.tds_percentage / 100
    if withdrawal_amount < coin:
        return 404, {
            "total_balance": user.coin,
            "withdrawal_amount": withdrawal_amount,
            "player_withdrawal": 0,
        }
    player_withdrawal = coin - (coin * tds_percentage)
    return 200, {
        "total_balance": user.coin,
        "withdrawal_amount": withdrawal_amount,
        "player_withdrawal": player_withdrawal,
    }

@transaction_api.get("/transaction-history", response={200: List[TransactionHistory], 409: Message})
async def transaction_history(request, transaction_type: str = 'credit'):
    user = request.auth
    if user.is_blocked:
        return 409, {"message": "Player blocked"}
    transaction_list = []
    async for transaction in TransactionLog.objects.filter(user=user, transaction_type=transaction_type).order_by('-id'):
        transaction_list.append(
            TransactionHistory(
                transaction_id=transaction.id,
                amount=transaction.amount,
                order_id=transaction.order_id,
                status=transaction.status
            )
        )
    return 200, transaction_list