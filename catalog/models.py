from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Shoes', 'Shoes'),
        ('Jersey', 'Jersey'),
        ('Ball', 'Ball'),
        ('Pants', 'Pants'),
        ('Accessories', 'Accessories'),
    ]

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)  # ✅ Tambahkan ini
    price = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField(default=0)
    image = models.URLField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.name
