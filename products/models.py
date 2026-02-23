from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def updateInfo(self, name=None, description=None, price=None):
        if name: self.name = name
        if description: self.description = description
        if price: self.price = price
        self.save()

    def updateBrand(self, brand):
        self.brand = brand
        self.save()

    def updateCategory(self, category):
        self.category = category
        self.save()

    def __str__(self):
        return self.name

class StockBySize(models.Model):
    productId = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_items')
    size = models.CharField(max_length=20)
    quantity = models.IntegerField(default=0)

    def increase(self, amount):
        self.quantity += amount
        self.save()

    def decrease(self, amount):
        if self.quantity >= amount:
            self.quantity -= amount
            self.save()
            return True
        return False

    def isAvailable(self):
        return self.quantity > 0

    def setQuantity(self, quantity):
        self.quantity = quantity
        self.save()

    def __str__(self):
        return f"{self.productId.name} - {self.size}: {self.quantity}"