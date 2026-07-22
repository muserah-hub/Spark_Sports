from django.shortcuts import render
from products.models import Product

def home(request):
    """
    Renders the Spark Sports homepage.
    Passes up to 3 featured products to the template context.
    """
    featured_products = Product.objects.filter(featured=True, available=True)[:3]
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'core/home.html', context)
