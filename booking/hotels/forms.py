from django import forms
from django.forms import HiddenInput, inlineformset_factory

from .models import HotelModel, RoomModel, PhotoModel


class HotelForm(forms.ModelForm):
    class Meta:
        model = HotelModel
        fields = ['name', 'country', 'city', 'location', 'description', 'rating', 'slug']


class PhotoForm(forms.ModelForm):
    class Meta:
        model = PhotoModel
        fields = ['photo_name', 'photo', 'hotel_id']


photo_for_hotel_inline_formset = inlineformset_factory(HotelModel, PhotoModel, form=PhotoForm, extra=3, can_delete_extra=True)

