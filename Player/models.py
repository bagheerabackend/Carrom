from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    first_name = None
    last_name = None
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10, unique=True)
    bonus = models.IntegerField()
    coin = models.IntegerField()
    avatar_no = models.IntegerField()
    profile_image = models.ImageField(upload_to="/icon", null=True, blank=True)