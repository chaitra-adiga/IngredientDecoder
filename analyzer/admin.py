from django.contrib import admin
from .models import Product, IngredientAnalysis

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'barcode', 'created_at')
    search_fields = ('name', 'barcode', 'ingredients_text')
    list_filter = ('category', 'created_at')

@admin.register(IngredientAnalysis)
class IngredientAnalysisAdmin(admin.ModelAdmin):
    list_display = ('product', 'overall_rating', 'analyzed_at')
    search_fields = ('product__name',)
    list_filter = ('overall_rating', 'analyzed_at')