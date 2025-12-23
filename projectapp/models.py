from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Kutilmoqda"),
        ("IN_PROGRESS", "Jarayonda"),
        ("DONE", "Tayyor"),
    ]

    # Buyurtma ma’lumotlari
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    service = models.CharField(max_length=255)
    price = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    topic = models.TextField()
    user_telegram_id = models.CharField(max_length=50)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    # ✅ CHEK
    receipt_file = models.FileField(
        upload_to="receipts/",
        null=True,
        blank=True
    )
    receipt_tg_file_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    # ✅ BAJARILGAN BUYURTMA
    result_file = models.FileField(
        upload_to="results/",
        null=True,
        blank=True
    )
    result_tg_file_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"
