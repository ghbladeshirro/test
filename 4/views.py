from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from models import Hotel
from serializers import HotelSerializer

class HotelListView(generics.ListAPIView):
    serializer_class = HotelSerializer
    
    def get_queryset(self):
        queryset = Hotel.objects.all()
        
        city = self.request.query_params.get('city')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if city:
            queryset = queryset.filter(city__iexact=city)
        
        if min_price:
            try:
                min_price = float(min_price)
                if min_price < 0:
                    raise ValidationError("min_price не может быть отрицательным")
                queryset = queryset.filter(price_per_night__gte=min_price)
            except ValueError:
                raise ValidationError("min_price должен быть числом")
        
        if max_price:
            try:
                max_price = float(max_price)
                if max_price < 0:
                    raise ValidationError("max_price не может быть отрицательным")
                queryset = queryset.filter(price_per_night__lte=max_price)
            except ValueError:
                raise ValidationError("max_price должен быть числом")
        
        if min_price and max_price and min_price > max_price:
            raise ValidationError("min_price не может быть больше max_price")
        
        return queryset.order_by('price_per_night')
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "count": queryset.count(),
                "results": serializer.data
            })
        except ValidationError as e:
            return Response({"error": e.detail}, status=400)