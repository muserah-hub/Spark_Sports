from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from products.models import Product

def checkout(request):
    """
    Renders checkout page and processes customer orders.
    Calculates prices server-side and deducts inventory stock levels.
    """
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Your cart is empty. Please add items before checking out.")
        return redirect('products:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            
            # Associate order with logged-in user if authenticated
            if request.user.is_authenticated:
                order.user = request.user
                
            # Server-side pricing calculation (never trust price values from the client)
            order.total_price = cart.get_total_price()
            order.payment_method = 'Cash on Delivery'
            order.save()
            
            # Save line items and deduct inventory levels
            for item in cart:
                product = item['product']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=item['price'],
                    quantity=item['quantity']
                )
                # Deduct inventory stock
                product.stock -= item['quantity']
                # If product runs out of stock, toggle availability
                if product.stock <= 0:
                    product.available = False
                product.save()
                
            # Clear shopping cart from session
            cart.clear()
            
            # Save order ID in session for the confirmation page
            request.session['order_id'] = order.id
            messages.success(request, "Your order has been placed successfully!")
            return redirect('orders:order_success')
        else:
            messages.error(request, "Order submission failed. Please check the form errors.")
    else:
        # Pre-populate form fields if user is authenticated
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.username,
                'email': request.user.email
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})


def order_success(request):
    """
    Renders order success page.
    """
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('home')
        
    order = get_object_or_404(Order, id=order_id)
    
    # Flush order ID from session so they can't reload and bypass
    if 'order_id' in request.session:
        del request.session['order_id']
        
    return render(request, 'orders/success.html', {'order': order})


def order_detail(request, order_id):
    """
    Displays shipping information and products for a single past order.
    Restricts access to authenticated owners.
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Security constraint: user must own the order if logged in, or prevent unauthorized view
    if order.user and order.user != request.user:
        raise PermissionDenied("You are not authorized to view this order details page.")
        
    return render(request, 'orders/detail.html', {'order': order})
