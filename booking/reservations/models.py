from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateRangeField, RangeOperators, RangeBoundary
from django.db import models
from django.db.models import Q, Func
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from hotels.models import RoomModel, HotelModel


class DateRange(Func):
    function = "DATERANGE"
    output_field = DateRangeField()


class BookingModel(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
    room_id = models.ForeignKey(RoomModel, on_delete=models.CASCADE, verbose_name='Room')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_reservations",
                expressions=[
                    (
                        DateRange("check_in_date", "check_out_date", RangeBoundary()),
                        RangeOperators.OVERLAPS,
                    ),
                    ("room_id", RangeOperators.EQUAL),
                ],
                condition=Q(cancelled=False),
            ),
        ]

    def __str__(self):
        return f'Booking {self.room_id} from {self.check_in_date} to {self.check_out_date} by {self.user_id}.'


class ReviewModel(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hotel_id = models.ForeignKey(HotelModel, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'Comment by {self.user_id} to hotel {self.hotel_id}.'
