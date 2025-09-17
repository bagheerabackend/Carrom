from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Matches
from django.dispatch import Signal
from Matches.utils.timer import start_disconnection_timer

player_disconnected_signal = Signal()

@receiver(player_disconnected_signal)
def handle_player_disconnected(sender, **kwargs):
    match_id = kwargs.get('match_id')
    player_id = kwargs.get('player_id')
    start_disconnection_timer(match_id, player_id, timeout_seconds=10)
