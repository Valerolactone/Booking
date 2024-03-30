from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Avg
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from django.db import transaction, DatabaseError
from .models import HotelModel, RoomModel, PhotoModel
from reservations.forms import CommentForm, ReservationForm
from reservations.models import ReviewModel


class ListHotelsView(ListView):
    paginate_by = 3
    model = HotelModel
    template_name = 'hotels/list_hotels.html'
    context_object_name = 'hotels'

    def get_queryset(self):
        return HotelModel.objects.prefetch_related(
            Prefetch('photos', queryset=PhotoModel.objects.filter(photo_name='cover')))


class HotelInfoView(View):
    def get(self, request, slug):
        hotel = get_object_or_404(HotelModel, slug=slug)
        photos = PhotoModel.objects.filter(hotel_id=hotel.id)
        rooms = RoomModel.objects.filter(hotel_id=hotel.id, available=True)
        reviews = ReviewModel.objects.filter(hotel_id=hotel.id).order_by('-created_at')
        user_hotel_rating = reviews.aggregate(Avg('rating'))
        comment_form = CommentForm()
        return render(request, 'hotels/certain_hotel.html',
                      context={'hotel': hotel, 'photos': photos,
                               'rooms': rooms, 'reviews': reviews,
                               'comment_form': comment_form,
                               'user_hotel_rating': user_hotel_rating})

    def post(self, requests, slug):
        comment_form = CommentForm(requests.POST)
        if comment_form.is_valid():
            comment_form.save()
            return redirect('hotel_info', slug=slug)


class RoomInfoView(View):
    def get(self, request, slug):
        room = get_object_or_404(RoomModel, slug=slug)
        photos = PhotoModel.objects.filter(room_id=room.id)
        reservation_form = ReservationForm()
        return render(request, 'hotels/certain_room.html',
                      context={'room': room, 'photos': photos, 'reservation_form': reservation_form})

    def post(self, requests, slug):
        room = get_object_or_404(RoomModel, slug=slug)
        reservation_form = ReservationForm(requests.POST)
        try:
            with transaction.atomic():
                if reservation_form.is_valid():
                    reservation_form.save()
        except DatabaseError:
            print('db error')
        except ValidationError:
            print('validation error')

        return redirect('room_info', slug=slug)
