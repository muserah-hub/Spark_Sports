from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .cart import Cart

@require_POST
def cart_add(request, product_id):
    """
    Handles adding products to the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    if quantity <= 0:
        messages.error(request, "Invalid quantity specified.")
        return redirect('products:product_list')

    # Add item to session cart
    cart.add(product=product, quantity=quantity)
    messages.success(request, f"Added {product.name} to your cart successfully!")
    
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    """
    Handles removing products from the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f"Removed {product.name} from your cart.")
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    """
    Handles updates to cart item quantities.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        quantity = int(request.POST.get('quantity'))
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity.")
        return redirect('cart:cart_detail')

    if quantity <= 0:
        cart.remove(product)
        messages.info(request, f"Removed {product.name} from your cart.")
    else:
        # Check stock boundaries
        if quantity > product.stock:
            quantity = product.stock
            messages.warning(request, f"We only have {product.stock} units of {product.name} in stock. Quantity updated to max available.")
        
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, f"Updated quantity for {product.name}.")

    return redirect('cart:cart_detail')


def cart_detail(request):
    """
    Renders the cart detail list page showing subtotal and shipping costs.
    """
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})
