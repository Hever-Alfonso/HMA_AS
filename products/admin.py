from django.contrib import admin
from .models import Product, StockBySize, Category

class StockBySizeInline(admin.TabularInline):
    model = StockBySize
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price')
    list_filter = ('brand', 'category')
    search_fields = ('name', 'description', 'brand', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [StockBySizeInline]

@admin.register(StockBySize)
class StockBySizeAdmin(admin.ModelAdmin):
    list_display = ('productId', 'size', 'quantity')
    list_filter = ('size',)
    search_fields = ('productId__name',)