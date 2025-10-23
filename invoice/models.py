import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from catalog.models import Product


# Create your models here.

class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    date = models.DateField(default=timezone.now)
    invoice_no = models.CharField(max_length=32, unique=True, db_index=True)

class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    date = models.DateField(default=timezone.now)
    invoice_no = models.CharField(max_length=32, unique=True, db_index=True)