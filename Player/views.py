from ninja import Router, PatchDict
from .schema import *
from typing import *
from .models import *
from .utils.verify_mail import send_otp_to_email
from ninja_jwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from asgiref.sync import sync_to_async
from ninja_jwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
import random
from Matches.models import Matches

user_api = Router(tags=["User"])

################################################ Register User ################################################
@user_api.post("/send-otp", auth=None, response={200: Message, 404: Message})
async def send_otp(request, data: OtpIn):
    if await Player.objects.filter(email=data.email).aexists():
        return 404, {"message": "Email already exists"}
    if await sync_to_async(cache.get)(data.email):
        await sync_to_async(cache.delete)(data.email)
    otp = random.randint(1000, 9999)
    print(otp)
    await sync_to_async(cache.set)(data.email, otp, timeout=60)
    await send_otp_to_email(data.email, otp)
    return 200, {"message": "OTP sent to email"}

@user_api.post("/verify-otp", auth=None, response={201: TokenOut, 404: Message, 405: Message, 409: Message})
async def verify_otp(request, data: OtpVerify):
    cached_otp = await sync_to_async(cache.get)(data.email)
    if cached_otp is None:
        return 404, {"message": "OTP expired or not found"}
    if cached_otp != data.otp:
        return 405, {"message": "Invalid OTP"}
    if await Player.objects.filter(Q(email=data.email) | Q(phone=data.phone)).aexists():
        return 409, {"message": "User with this email or phone already exists"}
    player_id = f"CRM0000001" if await Player.objects.acount() == 0 else f"CRM{(await Player.objects.alast()).id + 1:07d}"
    user = Player(
        player_id=player_id,
        name=data.name,
        username=data.email,
        email=data.email,
        phone=data.phone,
        age=data.age,
        avatar_no=random.randint(1, 10)
    )
    user.set_password(data.password)
    await user.asave()
    refresh = str(RefreshToken.for_user(user))
    access = str(AccessToken.for_user(user))
    await sync_to_async(cache.delete)(data.email)
    return 201, {"access": access, "refresh": refresh}

################################################ Login User ################################################
@user_api.post("/login", auth=None, response={200: TokenOut, 405: Message})
async def login(request, data: LoginIn):
    if not await Player.objects.filter(username=data.username).aexists():
        return 405, {"message": "Invalid credentials"}
    user = await Player.objects.aget(username=data.username)
    if not user.check_password(data.password):
        return 405, {"message": "Invalid credentials"}
    refresh = str(RefreshToken.for_user(user))
    access = str(AccessToken.for_user(user))
    return 200, {"access": access, "refresh": refresh}

@user_api.post("/refresh", auth=None, response={200: TokenOut, 405: Message})
async def refresh_token(request, data: RefreshTokenIn):
    try:
        refresh = RefreshToken(data.refresh)
        user = await Player.objects.aget(id=refresh['user_id'])
        # new_refresh = str(RefreshToken.for_user(user))
        new_access = str(AccessToken.for_user(user))
        return 200, {"access": new_access, "refresh": ""}
    except Exception as e:
        return 405, {"message": "Invalid refresh token"}
    
################################################ Change Password ################################################
@user_api.patch("/change-password", response={200: Message, 405: Message})
async def change_password(request, data: ChangePasswordIn):
    user = request.auth
    if check_password(data.password, user.password):
        return 405, {"message": "New password cannot be the same as the old password"}
    user.set_password(data.password)
    await user.asave()
    return 200, {"message": "Password changed successfully"}

################################################ Get Coin Details ################################################
@user_api.get("/coin-details", response={200: BonusOut})
async def coin_details(request):
    user = request.auth
    return 200, {"bonus": user.bonus, "coin": user.coin}

################################################ Profile Panel ################################################
@user_api.get("/profile-details", response={200: PlayerOut})
async def get_profile(request):
    user = request.auth
    total_count = await Matches.objects.filter(Q(player1=user) | Q(player2=user)).acount()
    winning_count = await Matches.objects.filter(winner=user).acount()
    losing_count = total_count - winning_count
    return 200, PlayerOut(
        player_id=user.player_id,
        name=user.name,
        avatar_no=user.avatar_no,
        total_games=total_count,
        total_wons=winning_count,
        total_loss=losing_count
    )