from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import HotelModel, RoomModel, PhotoModel


class HotelForm(forms.ModelForm):
    class Meta:
        model = HotelModel
        fields = ['name', 'country', 'city', 'location', 'rating', 'slug', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 15}),
        }


class RoomForm(forms.ModelForm):
    price_per_night = forms.DecimalField()

    class Meta:
        model = RoomModel
        fields = ['hotel_id', 'room_type', 'number', 'price_per_night', 'slug', 'available', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 15}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price_per_night = cleaned_data.get('price_per_night')

        if price_per_night < 0:
            raise ValidationError("The price can't be negative.")

        return cleaned_data


class PhotoForm(forms.ModelForm):
    class Meta:
        model = PhotoModel
        fields = ['photo_name', 'photo']


HotelPhotoFormSet = inlineformset_factory(HotelModel, PhotoModel, form=PhotoForm, can_delete=True,
                                          can_delete_extra=True)
RoomPhotoFormSet = inlineformset_factory(RoomModel, PhotoModel, form=PhotoForm, can_delete=True, can_delete_extra=True)
