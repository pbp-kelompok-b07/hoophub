from django.db import models
import uuid
# Create your models here.
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('tops', 'Tops'),
        ('legwear', 'Legwear'),
        ('jaket', 'Jaket'),
        ('shoes', 'Shoes'),
        ('basketball', 'Basketball'),
        ('equipment', 'Equipment'),
    ]

    BRAND_CHOICES = [
        ('nike', 'Nike'),
        ('adidas', 'Adidas'),
        ('tarmak', 'Tarmak'),
        ('wilson', 'Wilson'),
        ('spalding', 'Spalding'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='equipment')
    thumbnail = models.URLField(blank=True, null=True)
    price = models.PositiveIntegerField(default=0)
    brand = models.CharField(max_length=20,choices=BRAND_CHOICES, default='nike')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name