from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.forms.fields import DateField
from django.forms.widgets import DateInput, SelectDateWidget
from django.contrib.postgres.forms.ranges import DateRangeField
from .models import ReviewModel, BookingModel


class CommentForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = ['rating', 'comment', 'hotel_id', 'user_id']
        widgets = {
            'rating': forms.NumberInput(attrs={'max': 5, 'min': 1}),
            'comment': forms.Textarea(attrs={'cols': 100, 'rows': 10}),
            'hotel_id': HiddenInput(),
            'user_id': HiddenInput(),
        }


class ReservationDateInput(DateInput):
    input_type = 'date'


class ReservationDateField(DateField):
    widget = ReservationDateInput


class ReservationRangeDateField(DateRangeField):
    base_field = ReservationDateField


class ReservationForm(forms.ModelForm):
    booking_range = SelectDateWidget(range(1940, 2014))

    class Meta:
        model = BookingModel
        fields = ['user_id', 'room_id', 'booking_range', 'cancelled']
        widgets = {
            'user_id': HiddenInput(),
            'room_id': HiddenInput(),
            'cancelled': HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        room_id = cleaned_data.get('room_id')
        booking_range = cleaned_data.get('booking_range')
        all_booked_ranges = BookingModel.objects.filter(room_id=room_id).values('booking_range')
        print(f'{all_booked_ranges}wefewfewf')

        return cleaned_data


"""        if booking_range[0] < datetime.now():
            raise ValidationError("The check-in date cannot be in the past.")
        elif booking_range[1] < booking_range[0]:
            raise ValidationError("The check-out date cannot be earlier than the check-in date.")"""
