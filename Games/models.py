from django.db import models

class Game(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="game_image/", null=True, blank=True)
    fee = models.IntegerField()
    winning_amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name