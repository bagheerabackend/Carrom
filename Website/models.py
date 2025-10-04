from django.db import models

class WebGames(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    bg_image = models.ImageField(upload_to="website/bg")
    game_image = models.ImageField(upload_to="website/game")
    live = models.BooleanField(default=False)
    playstore_url = models.CharField(max_length=200)
    appstore_url = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

class ContactUsWeb(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=254)
    phone = models.CharField(max_length=10)
    message = models.TextField()
    contacted_on = models.DateField(auto_now_add=True)