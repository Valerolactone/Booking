from datetime import datetime
from django.contrib.postgres.forms.ranges import DateRangeField
from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput

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


class ReservationForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        room_id = cleaned_data.get('room_id')
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')

        if check_in_date < datetime.now():
            raise ValidationError("The check-in date cannot be in the past.")
        elif check_out_date < check_in_date:
            raise ValidationError("The check-out date cannot be earlier than the check-in date.")

        return cleaned_data

    class Meta:
        model = BookingModel
        fields = ['user_id', 'room_id', 'check_in_date', 'check_out_date']
        widgets = {
            'user_id': HiddenInput(),
            'room_id': HiddenInput(),
            'check_in_date': DateRangeField(),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }
