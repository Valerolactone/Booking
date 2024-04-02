from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.forms.fields import DateField
from django.forms.widgets import DateInput
from .models import ReviewModel, BookingModel


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

        if check_in_date < datetime.now().date():
            raise ValidationError("You can't book past dates.")

        return cleaned_data

"""    def save(self):
        instance = super(ReservationForm, self).save()
        a = self.cleaned_data["user_id"].email
        print(a)

        @transaction.on_commit
        def send_booking_email():
            message = f"generate the message from the {instance}"
            send_mail(
                "Subject here",
                message,
                "from@example.com",
                [self.cleaned_data["user_id"].email],
                fail_silently=False,
            )

        return instance"""
