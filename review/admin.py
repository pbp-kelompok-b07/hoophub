from django.contrib import admin
from .models import Review

# Register your models here.
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'date')
    list_filter = ('rating', 'date')
    search_fields = ('review', 'user__username', 'product__name')
    readonly_fields = ('user', 'product', 'date', 'id')

admin.site.register(Review, ReviewAdmin)