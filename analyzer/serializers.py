from rest_framework import serializers
from .models import Product, IngredientAnalysis

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'barcode', 'ingredients_text', 'created_at']

class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientAnalysis
        fields = ['id', 'product', 'analysis_json', 'overall_rating', 'analyzed_at']