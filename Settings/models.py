from django.db import models

class AppSettings(models.Model):
    version = models.CharField(max_length=20)
    force_update = models.BooleanField(default=False)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(null=True, blank=True)
    gst_percentage = models.FloatField(default=0.0)
    tds_percentage = models.FloatField(default=0.0)
    bonus_point = models.IntegerField(default=0)
    withdrawal_limit = models.IntegerField(default=0)
    daily_withdraw_count = models.IntegerField(default=0)
    # states_blacklisted = models.JSONField(default=[])