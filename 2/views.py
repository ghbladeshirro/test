# Обработка HTTP запросов: получение данных из БД, передача в сериализатор, возврат ответа
from rest_framework import generics
from models import Product
from serializers import ProductSerializer

# GET /products/ - список товаров
# POST /products/ - создание товара
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# GET /products/1/ - детали товара
# PUT /products/1/ - полное обновление
# PATCH /products/1/ - частичное обновление
# DELETE /products/1/ - удаление
class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer