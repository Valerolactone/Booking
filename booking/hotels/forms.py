from django import forms
from django.forms import HiddenInput, inlineformset_factory

from .models import HotelModel, RoomModel, PhotoModel


class HotelForm(forms.ModelForm):
    class Meta:
        model = HotelModel
        fields = ['name', 'country', 'city', 'location', 'description', 'rating', 'slug']


class RoomForm(forms.ModelForm):
    class Meta:
        model = RoomModel
        fields = ['hotel_id', 'room_type', 'number', 'description', 'price_per_night', 'slug', 'available']


class PhotoForm(forms.ModelForm):
    class Meta:
        model = PhotoModel
        fields = ['photo_name', 'photo']


HotelPhotoFormSet = inlineformset_factory(HotelModel, PhotoModel, form=PhotoForm, can_delete=True, can_delete_extra=True)
RoomPhotoFormSet = inlineformset_factory(RoomModel, PhotoModel, form=PhotoForm, can_delete=True, can_delete_extra=True)
