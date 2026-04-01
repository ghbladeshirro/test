# Маршруты: связь URL с функциями-обработчиками
from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDestroyView

urlpatterns = [
    # GET и POST на /products/
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    # GET, PUT, PATCH, DELETE на /products/1/
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
]