from django.contrib import admin
from .models import Wishlist

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    # kolom yang tampil di changelist (daftar)
    list_display = ('user', 'product', 'date_added')
    # filter di sidebar
    list_filter = ('date_added', 'user', 'product')
    # bidang yang bisa dicari via search box
    search_fields = ('user__username', 'user__email', 'product__name', 'product__brand')
    # tampilkan tanggal di atas untuk navigasi cepat per tanggal
    date_hierarchy = 'date_added'
    # field yang readonly di form change view
    readonly_fields = ('date_added',)
    # gunakan raw_id_fields untuk relasi yang potensial besar (hindari dropdown besar)
    raw_id_fields = ('user', 'product')
    # join/select related agar list queries efisien (hindari N+1)
    list_select_related = ('user', 'product')
    # opsi paging
    list_per_page = 25
    # urutan default
    ordering = ('-date_added',)

    def product_brand(self, obj):
        return getattr(obj.product, 'brand', '')
    product_brand.short_description = 'Brand'
