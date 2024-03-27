from django.contrib import admin
from .models import HotelModel, RoomModel, PhotoModel


@admin.register(PhotoModel)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['photo_name', 'photo', 'uploaded_at', 'hotel_id', 'room_id']
    exclude = ['uploaded_at', ]
    ordering = ['uploaded_at']


class PhotoInline(admin.StackedInline):
    model = PhotoModel
    max_num = 10
    extra = 0


@admin.register(HotelModel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'location', 'description',
                    'created_at', 'updated_at', 'deleted_at', 'deleted']
    exclude = ['created_at', 'updated_at', 'deleted_at', 'deleted']
    inlines = [PhotoInline, ]
    ordering = ['name']
    prepopulated_fields = {'slug': ('rating', 'name',)}


@admin.register(RoomModel)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hotel_id', 'number', 'room_type', 'price_per_night', 'available',
                    'created_at', 'updated_at', 'deleted_at', 'deleted']
    exclude = ['created_at', 'updated_at', 'deleted_at', 'deleted']
    inlines = [PhotoInline, ]
    prepopulated_fields = {'slug': ('number', 'room_type',)}
