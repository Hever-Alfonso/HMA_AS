from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    userId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    orderDate = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculateTotal(self):
        from decimal import Decimal
        self.totalAmount = sum((item.calculateSubtotal() for item in self.items.all()), Decimal('0.00'))
        self.save()
        return self.totalAmount

    def cancel(self):
        self.status = 'cancelled'
        self.save()

    def markAsPaid(self):
        self.status = 'paid'
        self.save()

    def __str__(self):
        return f"Order {self.id} - {self.userId}"
    
    # Shipping information
    shippingAddress = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postalCode = models.CharField(max_length=10, blank=True)
    contactPhone = models.CharField(max_length=15, blank=True)

    shippingCost = models.DecimalField(
       max_digits=10,
        decimal_places=2,
       default=0
    )

    trackingNumber = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

class OrderItem(models.Model):
    orderId = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    quantity = models.IntegerField()
    unitPrice = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def calculateSubtotal(self):
        self.subtotal = self.quantity * self.unitPrice
        self.save()
        return self.subtotal

    def __str__(self):
        return f"{self.productId.name} ({self.size}) x {self.quantity}"
