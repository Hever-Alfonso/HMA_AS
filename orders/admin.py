from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'userId', 'orderDate', 'status', 'totalAmount')
    list_filter = ('status', 'orderDate')
    search_fields = ('id', 'userId__username', 'userId__fullName')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('orderId', 'productId', 'size', 'quantity', 'unitPrice', 'subtotal')
