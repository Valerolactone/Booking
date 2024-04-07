from django.urls import path
from .views import BookingInfoView, ListReviews, ListRelevantBookings, AnalyticsView

urlpatterns = [
    path('<pk>/', BookingInfoView.as_view(), name='booking_info'),
    path('manage/reviews/', ListReviews.as_view(), name='all_reviews'),
    path('manage/bookings/', ListRelevantBookings.as_view(), name='all_bookings'),
    path('manage/analytics/', AnalyticsView.as_view(), name='analytics'),
]