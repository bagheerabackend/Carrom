from django.db import models
from Player.models import Player

class TransactionLog(models.Model):
    user = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.IntegerField()
    order_id = models.CharField(max_length=100, blank=True, null=True)
    gst_deduct = models.FloatField()
    balance_after = models.IntegerField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending')
    transaction_type = models.CharField(max_length=50, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    transaction_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"