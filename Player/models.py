from django.db import models
from django.contrib.auth.models import AbstractUser

class Player(AbstractUser):
    first_name = None
    last_name = None
    player_id = models.TextField()
    name = models.CharField(max_length=50)
    age = models.IntegerField(default=0)
    phone = models.CharField(max_length=10, default="")
    bonus = models.IntegerField(default=0)
    cashback = models.FloatField(default=0.0)
    coin = models.IntegerField(default=0)
    withdrawable_coin = models.IntegerField(default=0)
    game_coin_used = models.IntegerField(default=0)
    # aadhar_no = models.CharField(max_length=12, unique=True, null=True, blank=True)
    # aadhar_verified = models.BooleanField(default=False)
    pan_no = models.CharField(max_length=10, unique=True, null=True, blank=True)
    avatar_no = models.IntegerField()
    profile_image = models.ImageField(upload_to="profile_image/", null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='player_set',  # Custom related_name
        help_text='The groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='player_set',  # Custom related_name
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return self.username
    
class BankDetails(models.Model):
    user = models.ForeignKey(Player, on_delete=models.CASCADE)
    account_no = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=50)
    branch_name = models.CharField(max_length=50)
    holder_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BankDetails of {self.user.username}"