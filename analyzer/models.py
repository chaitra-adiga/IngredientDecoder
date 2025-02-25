from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food Product'),
        ('beauty', 'Beauty Product'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    ingredients_text = models.TextField()
    ingredients_image = models.ImageField(upload_to='ingredients_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class IngredientAnalysis(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='analysis')
    analysis_json = models.JSONField()
    overall_rating = models.IntegerField()  # 1-10 scale
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis for {self.product.name}"
