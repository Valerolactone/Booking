from datetime import datetime, timedelta
import pandas as pd
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.forms import HiddenInput
from django.forms.fields import DateField
from django.forms.widgets import DateInput
from .models import ReviewModel, BookingModel
from .services import get_unavailable_dates


class CommentForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = ['rating', 'comment', 'hotel_id', 'user_id']
        widgets = {
            'rating': forms.NumberInput(attrs={'max': 5, 'min': 0, 'class': 'form-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-input'}),
            'hotel_id': HiddenInput(),
            'user_id': HiddenInput(),
        }


class ReservationDateInput(DateInput):
    input_type = 'date'


class ReservationDateField(DateField):
    widget = ReservationDateInput


class ReservationForm(forms.ModelForm):
    check_in_date = ReservationDateField()
    check_out_date = ReservationDateField()

    class Meta:
        model = BookingModel
        fields = ['user_id', 'room_id', 'check_in_date', 'check_out_date', 'cancelled']
        widgets = {
            'user_id': HiddenInput(),
            'room_id': HiddenInput(),
            'cancelled': HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')

        if check_in_date < datetime.now().date():
            raise ValidationError("You can't book past dates.")

        if check_in_date == check_out_date:
            raise ValidationError("The dates have to be different.")

        if check_in_date > check_out_date:
            raise ValidationError("The booking check-out date cannot be earlier than the booking check-in date.")

        return cleaned_data

    def save(self):
        instance = super(ReservationForm, self).save()

        @transaction.on_commit
        def send_booking_confirmation_email():
            send_mail(
                subject='Booking Confirmation',
                message=f'We are confirming your {instance.room_id.number}-{instance.room_id.room_type} hotel room '
                        f'reservation in {instance.room_id.hotel_id.name} from the {instance.check_in_date} '
                        f'through the {instance.check_out_date}.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[self.cleaned_data["user_id"].email],
                fail_silently=False,
            )

        return instance


class UpdateReservationForm(forms.ModelForm):
    check_in_date = ReservationDateField()
    check_out_date = ReservationDateField()

    class Meta:
        model = BookingModel
        fields = ['check_in_date', 'check_out_date']

    def clean(self):
        cleaned_data = super().clean()
        new_check_in_date = cleaned_data.get('check_in_date')
        new_check_out_date = cleaned_data.get('check_out_date')
        unavailable_dates = get_unavailable_dates(self.instance.room_id)
        old_booking_dates = pd.date_range(self.instance.check_in_date, self.instance.check_out_date)
        old_booking_period = [date.date() for date in old_booking_dates]

        if new_check_in_date < datetime.now().date():
            raise ValidationError("You can't book past dates.")

        if new_check_in_date == new_check_out_date:
            raise ValidationError("The dates have to be different.")

        if new_check_in_date > new_check_out_date:
            raise ValidationError("The booking check-out date cannot be earlier than the booking check-in date.")

        for date in old_booking_period:
            if date in unavailable_dates:
                unavailable_dates.remove(date)

        while new_check_in_date <= new_check_out_date:
            if new_check_in_date in unavailable_dates:
                raise ValidationError("Those dates are already booked.")
            new_check_in_date += timedelta(days=1)

        return cleaned_data

    def save(self):
        instance = super(UpdateReservationForm, self).save()

        @transaction.on_commit
        def send_booking_confirmation_email():
            send_mail(
                subject='Update Booking Confirmation',
                message=f'We are confirming that your {instance.room_id.number}-{instance.room_id.room_type} hotel room '
                        f'reservation in {instance.room_id.hotel_id.name} has had the dates changed. New booking dates '
                        f' from {instance.check_in_date} to {instance.check_out_date}.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[instance.user_id.email],
                fail_silently=False,
            )

        return instance
