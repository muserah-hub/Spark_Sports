from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    """
    Model representing a product category (e.g. Cricket Bats, Cricket Balls, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Auto-generate slug from name if not provided.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Return the URL for filtering products by this category.
        """
        return f"{reverse('products:product_list')}?category={self.slug}"


class Product(models.Model):
    """
    Model representing an individual cricket item.
    """
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Auto-generate slug from name if not provided.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Return the canonical product detail URL.
        """
        return reverse('products:product_detail', args=[self.slug])

    @property
    def is_in_stock(self):
        """
        Helper property to check stock level.
        """
        return self.stock > 0

    @property
    def get_price(self):
        """
        Return active price (discounted price if exists).
        """
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def saving_amount(self):
        """
        Returns the rupee discount saving if discount_price exists.
        """
        if self.discount_price and self.discount_price < self.price:
            return self.price - self.discount_price
        return 0
