from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    """
    Session-based shopping cart implementation.
    """
    def __init__(self, request):
        """
        Initialize the cart using the session storage.
        """
        self.session = request.session
        # Retrieve the cart dictionary from sessions
        cart = self.session.get('cart')
        if not cart:
            # Set up an empty cart dict in session
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.get_price)
            }
        
        # Enforce server-side inventory stock limit check
        new_quantity = quantity if override_quantity else self.cart[product_id]['quantity'] + quantity
        if new_quantity > product.stock:
            new_quantity = product.stock  # cap at maximum stock level
            
        self.cart[product_id]['quantity'] = new_quantity
        self.save()

    def save(self):
        """
        Mark the session as modified to trigger database save.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product completely from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Loop through items in the cart and query database to fetch real Product models.
        """
        product_ids = self.cart.keys()
        # Fetch the product instances from the database
        products = Product.objects.filter(id__in=product_ids)
        
        cart_copy = self.cart.copy()
        for product in products:
            cart_copy[str(product.id)]['product'] = product

        for item in cart_copy.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Sum up the quantity of all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal_price(self):
        """
        Compute cart subtotal.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_shipping_price(self):
        """
        Standard shipping cost across Pakistan.
        Free if total order is over Rs. 10,000.
        """
        subtotal = self.get_subtotal_price()
        if subtotal >= 10000 or subtotal == 0:
            return Decimal('0.00')
        return Decimal('250.00')  # Standard Flat Rate Rs. 250

    def get_total_price(self):
        """
        Compute total checkout price (subtotal + shipping).
        """
        return self.get_subtotal_price() + self.get_shipping_price()

    def clear(self):
        """
        Empty the cart session.
        """
        del self.session['cart']
        self.save()
