from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Shoes', 'Shoes'),
        ('Jersey', 'Jersey'),
        ('Ball', 'Ball'),
        ('Hoop', 'Hoop'),
        ('Accessories', 'Accessories'),
    ]

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField()
    image = models.URLField(max_length=300, blank=True, null=True)    
    # kolom tambahan
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, help_text="Average rating (0-5)")
    is_available = models.BooleanField(default=True)
    release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.brand})"