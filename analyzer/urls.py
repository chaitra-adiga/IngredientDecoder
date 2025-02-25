from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_ingredients, name='analyze_ingredients'),
    path('products/', views.product_history, name='product_history'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
]