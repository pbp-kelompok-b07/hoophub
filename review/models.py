import uuid
from django.db import models
from django.contrib.auth.models import User
# from catalog.models import Product

# Create your models here.
class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateTimeField(auto_now_add=True)
    review = models.TextField(blank=True, null=True)
    rating = models.IntegerField()
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, related_names='reviews')