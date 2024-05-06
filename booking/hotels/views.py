from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Prefetch, Avg, Func
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.db import transaction
from .models import HotelModel, RoomModel, PhotoModel, HotelStatisticsModel
from .forms import HotelForm, HotelPhotoFormSet, RoomForm, RoomPhotoFormSet
from reservations.forms import CommentForm, ReservationForm
from reservations.models import ReviewModel, BookingModel, DateRange
from reservations.services import get_unavailable_dates


class Round(Func):
    function = 'ROUND'
    template = "%(function)s(%(expressions)s::numeric, 1)"


class ListHotelsView(ListView):
    paginate_by = 3
    model = HotelModel
    template_name = 'hotels/list_hotels.html'
    context_object_name = 'hotels'

    def get_queryset(self):
        return HotelModel.objects.filter(deleted=False).prefetch_related(
            Prefetch('photos', queryset=PhotoModel.objects.filter(photo_name='cover'))).order_by('-created_at')


class HotelInline:
    form_class = HotelForm
    model = HotelModel
    template_name = 'hotels/create_or_update_hotel_or_room.html'

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('hotel_info', slug=self.object.slug)

    def formset_images_valid(self, formset):
        photos = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for photo in photos:
            photo.hotel_id = self.object
            photo.save()


class CreateHotelView(LoginRequiredMixin, UserPassesTestMixin, HotelInline, CreateView):

    def get_context_data(self, **kwargs):
        context = super(CreateHotelView, self).get_context_data(**kwargs)
        context['named_formsets'] = self.get_named_formsets()
        return context

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {'photos': HotelPhotoFormSet()}
        else:
            return {'photos': HotelPhotoFormSet(self.request.POST or None, self.request.FILES or None)}

    def test_func(self):
        return self.request.user.is_superuser


class UpdateHotelView(LoginRequiredMixin, UserPassesTestMixin, HotelInline, UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdateHotelView, self).get_context_data(**kwargs)
        context['named_formsets'] = self.get_named_formsets()
        return context

    def get_named_formsets(self):
        return {'photos': HotelPhotoFormSet(self.request.POST or None, self.request.FILES or None,
                                            instance=self.object, prefix='photos')}

    def test_func(self):
        return self.request.user.is_superuser


class HotelInfoView(CreateView):
    model = ReviewModel
    form_class = CommentForm
    template_name = 'hotels/certain_hotel.html'

    def get_context_data(self, **kwargs):
        context = super(HotelInfoView, self).get_context_data(**kwargs)
        hotel = get_object_or_404(HotelModel, slug=self.kwargs.get('slug'))
        rooms = RoomModel.objects.filter(hotel_id=hotel.id)
        reviews = ReviewModel.objects.filter(hotel_id=hotel.id).order_by('-created_at')
        current_date = datetime.now().date()
        bookings = BookingModel.objects.filter(room_id__in=rooms.values_list('id', flat=True))
        statistics = HotelStatisticsModel.objects.get(hotel=hotel.id)
        context['hotel'] = hotel
        context['rooms'] = rooms
        context['reviews'] = reviews
        context['current_date'] = current_date
        context['photos'] = PhotoModel.objects.filter(hotel_id=hotel.id)
        context['users_who_booked'] = bookings.distinct('user_id').values_list('user_id', flat=True)
        context['check_out_dates'] = bookings.filter(check_out_date__lte=current_date).values_list('check_out_date',
                                                                                                   flat=True)
        context['statistics'] = statistics

        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if request.POST.get('delete-button') and request.user.is_staff:
            hotel = get_object_or_404(HotelModel, slug=self.kwargs.get('slug'))
            hotel.deleted = True
            hotel.deleted_at = datetime.now()
            hotel.save()
            return redirect('hotels')
        if request.POST.get('comment-button') and form.is_valid():
            form.save()
            return redirect('hotel_info', slug=self.kwargs.get('slug'))
        else:
            return self.form_invalid(form, **kwargs)

    def form_invalid(self, form, **kwargs):
        self.object = None
        return self.render_to_response(
            self.get_context_data(form=form, **kwargs))


class RoomInline:
    form_class = RoomForm
    model = RoomModel
    template_name = 'hotels/create_or_update_hotel_or_room.html'

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('room_info', slug=self.object.slug)

    def formset_images_valid(self, formset):
        photos = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for photo in photos:
            photo.room_id = self.object
            photo.save()


class CreateRoomView(LoginRequiredMixin, UserPassesTestMixin, RoomInline, CreateView):

    def get_context_data(self, **kwargs):
        context = super(CreateRoomView, self).get_context_data(**kwargs)
        context['named_formsets'] = self.get_named_formsets()
        return context

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {'photos': HotelPhotoFormSet()}
        else:
            return {'photos': HotelPhotoFormSet(self.request.POST or None, self.request.FILES or None)}

    def test_func(self):
        return self.request.user.is_superuser


class UpdateRoomView(LoginRequiredMixin, UserPassesTestMixin, RoomInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(UpdateRoomView, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {'photos': RoomPhotoFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object)}

    def test_func(self):
        return self.request.user.is_superuser


class RoomInfoView(CreateView):
    model = BookingModel
    form_class = ReservationForm
    template_name = 'hotels/certain_room.html'

    def get_context_data(self, **kwargs):
        context = super(RoomInfoView, self).get_context_data(**kwargs)
        room = get_object_or_404(RoomModel, slug=self.kwargs.get('slug'))
        context['room'] = room
        context['unavailable_dates'] = get_unavailable_dates(room.id)
        context['photos'] = PhotoModel.objects.filter(room_id=room.id)

        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if request.POST.get('delete-button') and request.user.is_staff:
            room = get_object_or_404(RoomModel, slug=self.kwargs.get('slug'))
            room.deleted = True
            room.deleted_at = datetime.now()
            room.available = False
            room.save()
            return redirect('hotel_info', slug=room.hotel_id.slug)
        if request.POST.get('reservation-button') and form.is_valid():
            with transaction.atomic():
                form.save()
                return redirect('profile')
        else:
            return self.form_invalid(form, **kwargs)

    def form_invalid(self, form, **kwargs):
        self.object = None
        return self.render_to_response(
            self.get_context_data(form=form, **kwargs))
