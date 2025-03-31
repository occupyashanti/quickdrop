from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class Delivery(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('MPESA', 'M-Pesa'),
        ('CASH', 'Cash on Delivery'),
        ('CARD', 'Credit/Debit Card'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned'),
        ('PICKED_UP', 'Picked Up'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PACKAGE_TYPE_CHOICES = [
        ('document', 'Document'),
        ('parcel', 'Parcel'),
        ('fragile', 'Fragile'),
        ('perishable', 'Perishable'),
    ]

    # Core fields
    tracking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deliveries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Package details
    package_description = models.TextField()
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Pickup location details
    pickup_street = models.CharField(max_length=255)
    pickup_building = models.CharField(max_length=255, blank=True)
    pickup_city = models.CharField(max_length=100)
    pickup_area = models.CharField(max_length=100)
    pickup_landmark = models.CharField(max_length=255, blank=True)
    pickup_location = models.TextField(help_text="Formatted full address")
    
    # Delivery location details
    delivery_street = models.CharField(max_length=255)
    delivery_building = models.CharField(max_length=255, blank=True)
    delivery_city = models.CharField(max_length=100)
    delivery_area = models.CharField(max_length=100)
    delivery_landmark = models.CharField(max_length=255, blank=True)
    delivery_location = models.TextField(help_text="Formatted full address")
    
    # Contact information
    sender_name = models.CharField(max_length=100)
    sender_phone = models.CharField(max_length=15)
    recipient_name = models.CharField(max_length=100)
    recipient_phone = models.CharField(max_length=15)
    delivery_notes = models.TextField(blank=True)
    
    # Payment information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_date = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Delivery status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    assigned_driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_deliveries')
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Worker rating
    worker_rating = models.IntegerField(null=True, blank=True, help_text="Rating from 1-5 stars")
    worker_rating_comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Deliveries'

    def __str__(self):
        return f"Delivery {self.order_id} - {self.status}"

    def save(self, *args, **kwargs):
        # Format full addresses if not already set
        if not self.pickup_location and all([self.pickup_street, self.pickup_city, self.pickup_area]):
            self.pickup_location = f"{self.pickup_street}, {self.pickup_building + ', ' if self.pickup_building else ''}{self.pickup_area}, {self.pickup_city}"
            if self.pickup_landmark:
                self.pickup_location += f" (Near {self.pickup_landmark})"

        if not self.delivery_location and all([self.delivery_street, self.delivery_city, self.delivery_area]):
            self.delivery_location = f"{self.delivery_street}, {self.delivery_building + ', ' if self.delivery_building else ''}{self.delivery_area}, {self.delivery_city}"
            if self.delivery_landmark:
                self.delivery_location += f" (Near {self.delivery_landmark})"

        super().save(*args, **kwargs)
