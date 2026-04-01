# Валидация данных и преобразование JSON ↔ БД
from rest_framework import serializers
from models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Остаток не может быть отрицательным")
        return value