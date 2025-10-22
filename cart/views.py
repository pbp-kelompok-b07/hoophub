from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from cart.models import Product


# Create your views here.
def show_cart(request):
    # cart_data = request.session.get('cart', {})
    
    # cart_items = []
    # total_cart_price = 0
    
    # for product_id in cart_data.items():
    #     try:
    #         product = Product.objects.get(id=product_id)            
    #         total_cart_price += product.price
            
    #         cart_items.append({
    #             'product': product,
    #             'id': product_id,
    #         })
    #     except Product.DoesNotExist:
    #         continue
            
    fake_product_1 = {
        'id': '123e4567-e89b-12d3-a456-426614174001',
        'name': 'Baju Basket Keren',
        'thumbnail': 'https://images.tokopedia.net/img/cache/900/VqbcmM/2022/1/19/22003c2d-9477-4467-b586-3f1396d2c4ea.jpg', # URL gambar asli
        'price': 150000,
        'description': 'Ini adalah deskripsi produk palsu pertama.'
    }

    fake_product_2 = {
        'id': '987e6543-e21b-32d1-a456-426614174002',
        'name': 'Sepatu Lari Cepat',
        'thumbnail': 'https://images.tokopedia.net/img/cache/900/VqbcmM/2023/12/12/f22e7b51-246e-444f-8e4d-c124a9e9e69c.jpg', # URL gambar asli
        'price': 750000,
        'description': 'Deskripsi produk palsu kedua untuk sepatu.'
    }

    # Ini adalah data 'cart_items' palsu
    hardcoded_cart_items = [
        {
            'id': '123e4567-e89b-12d3-a456-426614174001',
            'product': fake_product_1, # Data produk palsu
            'quantity': 2,
            'item_total': 300000
        },
        {
            'id': '987e6543-e21b-32d1-a456-426614174002',
            'product': fake_product_2, # Data produk palsu
            'quantity': 1,
            'item_total': 750000
        }
    ]

    context = {
        'cart_items': hardcoded_cart_items,
        'total_cart_price': 1050000,
    }
    
    return render(request, 'cart.html', context)

@require_POST
def delete_from_cart(request, id):
    product = get_object_or_404(Product, pk=id)
    product.delete()
    
    return HttpResponseRedirect(reverse('cart:show_cart'))

