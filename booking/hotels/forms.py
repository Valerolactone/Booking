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
        fields = ['photo_name', 'photo']


PhotoFormSet = inlineformset_factory(HotelModel, PhotoModel, form=PhotoForm, can_delete=True, can_delete_extra=True)
