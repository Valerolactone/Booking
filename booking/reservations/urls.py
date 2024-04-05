from django.urls import path
from .views import BookingInfoView

urlpatterns = [
    path('<pk>/', BookingInfoView.as_view(), name='booking_info'),
]