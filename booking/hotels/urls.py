from django.urls import path
from .views import ListHotelsView, HotelInfoView, RoomInfoView

urlpatterns = [
    path('', ListHotelsView.as_view(), name='hotels'),
    path('hotel/<slug:slug>', HotelInfoView.as_view(), name='hotel_info'),
    path('room/<slug:slug>', RoomInfoView.as_view(), name='room_info'),
]
