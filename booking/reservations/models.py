from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from hotels.models import RoomModel, HotelModel


class BookingModel(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
    room_id = models.ForeignKey(RoomModel, on_delete=models.CASCADE, verbose_name='Room')
    check_in_date = models.DateField(null=False, blank=False)
    check_out_date = models.DateField(null=False, blank=False)
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'Booking {self.room_id} from {self.check_in_date} to {self.check_out_date} by {self.user_id}.'


class ReviewModel(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hotel_id = models.ForeignKey(HotelModel, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'Comment by {self.user_id} to hotel {self.hotel_id}.'
