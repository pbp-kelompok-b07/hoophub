from django.db import models
from django.conf import settings
from catalog.models import Product

class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlists'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='in_wishlists'
    )
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_wishlist'),
        ]
        ordering = ['-date_added']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
