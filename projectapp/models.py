from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("payment_approved", "Payment Approved"),
        ("taken", "Taken"),
        ("ready", "Ready"),
    ]

    user_telegram_id = models.BigIntegerField()
    contact_phone = models.CharField(max_length=20)
    service_type = models.CharField(max_length=50)
    fullname = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    topic = models.TextField()
    price = models.IntegerField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    approved_by = models.CharField(max_length=100, null=True, blank=True)
    taken_by = models.CharField(max_length=100, null=True, blank=True)
    file_id = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
