from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from .utils.auth import AsyncJWTAuth
from Player.views import user_api
from Games.views import game_api
from Matches.views import match_api

api = NinjaAPI(auth=AsyncJWTAuth())

api.add_router("/user/", user_api)
api.add_router("/games/", game_api)
api.add_router("/matches/", match_api)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)