from django.db import models
class Delivery(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"

# Create your models here.
