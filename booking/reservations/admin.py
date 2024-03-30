from django.contrib import admin
from .models import BookingModel, ReviewModel


@admin.register(BookingModel)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'room_id', 'booking_range', 'cancelled', 'created_at', 'updated_at', 'deleted_at',
                    'deleted']
    exclude = ['cancelled', 'created_at', 'updated_at', 'deleted_at', 'deleted']
    ordering = ['-created_at']


@admin.register(ReviewModel)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'hotel_id', 'comment', 'rating', 'created_at', 'updated_at', 'deleted_at',
                    'deleted']
    exclude = ['created_at', 'updated_at', 'deleted_at', 'deleted']
    ordering = ['-created_at']
