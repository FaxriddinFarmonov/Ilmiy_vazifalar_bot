from django.db import models

from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed")
    ]

    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    service = models.CharField(max_length=100)
    price = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=255)
    topic = models.TextField()
    receipt_file_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="PENDING")
    accepted_by = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fullname} - {self.service}"
