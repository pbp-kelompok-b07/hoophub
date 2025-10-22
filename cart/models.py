from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product
import uuid

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Shipped', 'Shipped'),
        ('Cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username if self.user else 'Guest'}"