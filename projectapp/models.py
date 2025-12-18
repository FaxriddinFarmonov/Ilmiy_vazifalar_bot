from django.db import models
# projectapp/models.py
# projectapp/models.py

class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("IN_PROGRESS", "In progress"),
        ("DONE", "Done"),
    ]

    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    service = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    topic = models.TextField()
    price = models.CharField(max_length=50)

    receipt_file_id = models.CharField(max_length=255, null=True, blank=True)
    result_file_id = models.CharField(max_length=255, null=True, blank=True)

    user_telegram_id = models.BigIntegerField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    accepted_by = models.CharField(max_length=255, null=True, blank=True)
    taken_by = models.CharField(max_length=255, null=True, blank=True)
    completed_by = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.fullname}"
