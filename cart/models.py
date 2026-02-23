from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    userId = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    status = models.CharField(max_length=50, default='active')

    def addItem(self, product, size, quantity=1):
        item, created = CartItem.objects.get_or_create(cart=self, productId=product, size=size, defaults={'unitPrice': product.price})
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

    def removeItem(self, product, size):
        CartItem.objects.filter(cart=self, productId=product, size=size).delete()

    def updateItem(self, product, size, quantity):
        item = CartItem.objects.filter(cart=self, productId=product, size=size).first()
        if item:
            item.quantity = quantity
            item.save()

    def getTotal(self):
        from decimal import Decimal
        return sum((item.getSubtotal() for item in self.items.all()), Decimal('0.00'))

    def clear(self):
        self.items.all().delete()

    def __str__(self):
        return f"Cart {self.id} - {self.userId}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    quantity = models.IntegerField(default=1)
    unitPrice = models.DecimalField(max_digits=10, decimal_places=2)

    def getSubtotal(self):
        return self.quantity * self.unitPrice

    def __str__(self):
        return f"{self.productId.name} ({self.size}) x {self.quantity}"
