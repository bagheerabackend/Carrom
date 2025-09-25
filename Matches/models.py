from django.db import models
from Games.models import Game
from Player.models import Player

class Matches(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player1 = models.ForeignKey(Player, related_name='match_player1', on_delete=models.CASCADE)
    player1_disconnected = models.BooleanField(default=False)
    player2 = models.ForeignKey(Player, related_name='match_player2', on_delete=models.CASCADE, null=True, blank=True)
    player2_disconnected = models.BooleanField(default=False)
    winner = models.ForeignKey(Player, related_name='winner', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('waiting', 'Waiting'), ('full', 'Full'), ('completed', 'Completed')], default='waiting')
    winning_amount = models.IntegerField(null=True, blank=True)
    commission_amount = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match: {self.game.name} - Player1: {self.player1.name} vs Player2: {self.player2.name if self.player2 else "Player 2 not joined"} - Winner: {self.winner.name if self.winner else 'TBD'}"