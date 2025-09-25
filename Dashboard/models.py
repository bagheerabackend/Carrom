from django.db import models
from django.contrib.auth.models import AbstractUser

class AdminUser(AbstractUser):
    first_name = None
    last_name = None
    name = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='adminuser_set', 
        help_text='The groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='adminuser_set',
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return self.username