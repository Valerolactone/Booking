from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

ROOM_TYPES = (
    ('SGL', 'SGL'),
    ('DBL', 'DBL'),
    ('TWIN', 'TWIN'),
    ('TRPL', 'TRPL'),
    ('QDPL', 'QDPL'),
)


class HotelModel(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100, unique=True)
    location = models.CharField(null=False, blank=False, max_length=255, unique=True)
    description = models.TextField(null=False, blank=False, max_length=2000)
    rating = models.PositiveSmallIntegerField(null=False, blank=False, verbose_name='Stars',
                                              validators=[MinValueValidator(1), MaxValueValidator(5)])
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'A {self.rating}-star {self.name} hotel.'


class RoomModel(models.Model):
    hotel_id = models.ForeignKey(HotelModel, on_delete=models.CASCADE, verbose_name='Hotel')
    room_type = models.CharField(choices=ROOM_TYPES, max_length=10)
    number = models.PositiveIntegerField(unique=True)
    price_per_night = models.DecimalField(decimal_places=2, max_digits=8)
    available = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.number} {self.room_type}-room in the {self.hotel_id} hotel'


class PhotoModel(models.Model):
    photo_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    hotel_id = models.ForeignKey(HotelModel, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='photos', verbose_name='Hotel',
                                 help_text='Optional field')
    room_id = models.ForeignKey(RoomModel, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='photos', verbose_name='Room',
                                help_text='Optional field')

    def clean(self):
        if self.hotel_id and self.room_id:
            raise ValidationError(
                _(f'The image must relate to either the hotel "{self.hotel_id}" or the room "{self.room_id}".'))

    def save(self, *args, **kwargs):
        if self.hotel_id and self.room_id:
            return super(PhotoModel, self).clean()
        return super(PhotoModel, self).save(*args, **kwargs)

    def __str__(self):
        return self.photo_name
