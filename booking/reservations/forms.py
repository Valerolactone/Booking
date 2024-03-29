from django import forms
from django.forms import HiddenInput
from .models import ReviewModel


class CommentForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = ['rating', 'comment', 'hotel_id', 'user_id']
        widgets = {
            'hotel_id': HiddenInput(),
            'user_id': HiddenInput(),
        }
