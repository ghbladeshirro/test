from django.urls import path
from views import HotelListView

urlpatterns = [
    path('api/hotels/', HotelListView.as_view(), name='hotel-list'),
]