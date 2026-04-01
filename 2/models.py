# Описание структуры товара в базе данных
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)  # Название товара
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена
    stock = models.PositiveIntegerField(default=0)  # Остаток на складе
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)  # Дата обновления