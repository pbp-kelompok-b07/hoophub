from django.utils.html import format_html
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'is_available', 'release_date', 'preview_image')
    list_filter = ('brand', 'category', 'is_available')
    search_fields = ('name', 'brand', 'category')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:100px;"/>', obj.image)
        return "No image"
    preview_image.short_description = 'Preview'
