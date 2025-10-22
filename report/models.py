import uuid
from django.db import models
from django.contrib.auth.models import User
# from product.models import Product

# Create your models here.

class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
        
    REPORT_TYPE_CHOICES = [
        ('review', 'Review'),
        ('product', 'Product'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    # reported_product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_received", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    title = models.CharField(max_length=255)  # alasan singkat
    description = models.TextField(blank=True)  # penjelasan detail
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report by {self.reporter} on {self.reported_user} - {self.get_report_type_display()}"