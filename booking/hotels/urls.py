from django.urls import path
from .views import ListHotelsView, HotelInfoView, RoomInfoView, CreateHotelView, UpdateHotelView

urlpatterns = [
    path('', ListHotelsView.as_view(), name='hotels'),
    path('hotel/<slug:slug>', HotelInfoView.as_view(), name='hotel_info'),
    path('room/<slug:slug>', RoomInfoView.as_view(), name='room_info'),
    path('manage/add_hotel/', CreateHotelView.as_view(), name='add_hotel'),
    path('manage/update_hotel/<pk>', UpdateHotelView.as_view(), name='update_hotel'),
]
