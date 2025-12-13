from django.core.management.base import BaseCommand
from django.conf import settings
from decouple import config
from Settings.models import AppSettings
from Player.models import Player

class Command(BaseCommand):
    help = 'Recharge bonus for all users at midnight'

    def handle(self, *args, **kwargs):
        bonus_point = settings.BONUS_REFILL_POINT
        players = Player.objects.filter(is_blocked=False, bonus__lt=bonus_point).only('bonus')
        for player in players:
            player.bonus = bonus_point
            player.save()
        self.stdout.write(self.style.SUCCESS('Successfully recharged bonus for all users.'))