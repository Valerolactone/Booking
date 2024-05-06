from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from reservations.models import ReviewModel, BookingModel
from .models import HotelModel, HotelStatisticsModel


@receiver(post_save, sender=HotelModel)
def create_hotel_statistics(sender, instance, created, **kwargs):
    if created:
        HotelStatisticsModel.objects.create(hotel=instance)


@receiver(post_save, sender=ReviewModel)
def update_hotel_review_statistics(sender, instance, created, **kwargs):
    if created:
        HotelStatisticsModel.objects.filter(hotel=instance.hotel_id.id).update(
            total_number_of_reviews=F('total_number_of_reviews') + 1)
        HotelStatisticsModel.objects.filter(hotel=instance.hotel_id.id).update(
            user_rating=(instance.rating + (F('user_rating') * (F('total_number_of_reviews') - 1))) / F(
                'total_number_of_reviews'))


@receiver(post_save, sender=BookingModel)
def update_hotel_bookings_statistics(sender, instance, created, **kwargs):
    if created:
        HotelStatisticsModel.objects.filter(hotel=instance.room_id.hotel_id).update(
            total_number_of_bookings=F('total_number_of_bookings') + 1)
    else:
        if instance.deleted:
            HotelStatisticsModel.objects.filter(hotel=instance.room_id.hotel_id).update(
                total_number_of_bookings=F('total_number_of_bookings') - 1)
