from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from .models import Category, Product

def product_list(request):
    """
    Renders the catalog listing page.
    Supports filtering by category and basic search.
    """
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    sort_by = request.GET.get('sort')

    # Start with all available items
    products_list = Product.objects.filter(available=True).select_related('category')
    categories = Category.objects.all()
    selected_category = None

    # Filter by category
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products_list = products_list.filter(category=selected_category)

    # Filter by search text
    if search_query:
        products_list = products_list.filter(
            models.Q(name__icontains=search_query) | 
            models.Q(description__icontains=search_query)
        )

    # Filter by price range
    if price_min:
        try:
            products_list = products_list.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products_list = products_list.filter(price__lte=float(price_max))
        except ValueError:
            pass

    # Sort results
    if sort_by == 'price_low':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_high':
        products_list = products_list.order_by('-price')
    elif sort_by == 'newest':
        products_list = products_list.order_by('-created_at')
    else:
        # Default sort
        products_list = products_list.order_by('-created_at')

    # Pagination: 9 products per page
    paginator = Paginator(products_list, 9)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
        'selected_category': selected_category,
        'products': products,
        'sort_by': sort_by,
        'price_min': price_min,
        'price_max': price_max,
        'category_slug': category_slug,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """
    Renders a detailed view of a specific cricket product.
    Fetches up to 3 related products in the same category.
    """
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category, 
        available=True
    ).exclude(id=product.id)[:3]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)
