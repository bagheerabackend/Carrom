from ninja.security import HttpBearer
from Player.models import Player
import jwt
from django.conf import settings

class AsyncJWTAuth(HttpBearer):
    async def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if user_id and await Player.objects.filter(id=user_id).aexists():
                user = await Player.objects.aget(id=user_id)
                return user
            return None
        except jwt.ExpiredSignatureError:
            return None
        except Exception as e:
            return None