from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """
    Shows line items inline when inspecting an Order.
    """
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for Orders.
    """
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone', 'city', 'total_price', 'order_status', 'created_at']
    list_filter = ['order_status', 'created_at', 'updated_at']
    list_editable = ['order_status']
    search_fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'city']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    ordering = ['-created_at']
