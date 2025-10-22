from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from catalog.models import Product 
import json

def show_cart(request):
    cart_data = request.session.get('cart', {})
    
    cart_items = []
    total_cart_price = 0
    
    for product_id, item_data in cart_data.items():
        try:
            product = Product.objects.get(id=product_id)
            
            quantity = item_data.get('quantity', 1) 
            
            item_total = product.price * quantity
            total_cart_price += item_total
            
            cart_items.append({
                'product': product,
                'id': product_id,
                'quantity': quantity,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            if product_id in request.session['cart']:
                del request.session['cart'][product_id]
                request.session.modified = True
            continue
            
    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
    }
    
    return render(request, 'cart.html', context)

@require_POST
def remove_from_cart(request, item_id):

    cart = request.session.get('cart', {})
    
    product_id_str = str(item_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        
        request.session['cart'] = cart
        request.session.modified = True
        
    return HttpResponseRedirect(reverse('cart:show_cart'))

@require_POST
def add_to_cart(request, product_id):

    cart = request.session.get('cart', {})
    
    quantity = int(request.POST.get('quantity', 1))
    
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {'quantity': quantity}
        
    request.session['cart'] = cart
    
    return redirect(request.META.get('HTTP_REFERER', 'main:show_main'))