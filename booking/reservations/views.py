from datetime import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Avg, Count, Prefetch
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView

from .forms import UpdateReservationForm
from .models import BookingModel, ReviewModel
from hotels.models import PhotoModel, RoomModel, HotelModel
from .services import get_unavailable_dates
from hotels.views import Round


class BookingInfoView(LoginRequiredMixin, View):

    def get(self, request, pk):
        booking = get_object_or_404(BookingModel, pk=pk)
        photos = PhotoModel.objects.filter(room_id=booking.room_id)
        unavailable_dates = get_unavailable_dates(booking.room_id)
        current_date = datetime.now().date()
        price = (booking.check_out_date - booking.check_in_date).days * booking.room_id.price_per_night
        update_reservation_form = UpdateReservationForm(initial={'check_in_date': booking.check_in_date,
                                                                 'check_out_date': booking.check_out_date})
        return render(request, 'reservations/certain_reservation.html',
                      context={'photos': photos, 'booking': booking, 'price': price,
                               'update_reservation_form': update_reservation_form,
                               'unavailable_dates': unavailable_dates, 'current_date': current_date})

    def post(self, request, pk):
        booking = get_object_or_404(BookingModel, pk=pk)
        update_reservation_form = UpdateReservationForm(request.POST, instance=booking)
        if request.POST.get('update-button') and update_reservation_form.is_valid():
            update_reservation_form.save()
            return redirect('booking_info', pk)
        if request.POST.get('delete-button'):
            booking.deleted = True
            booking.cancelled = True
            booking.deleted_at = datetime.now()
            booking.save()
            if request.user.is_superuser:
                @transaction.on_commit
                def send_booking_confirmation_email():
                    send_mail(
                        subject='Cancellation of Booking',
                        message=f'We are sorry to inform you, but due to the circumstances  we have to cancel '
                                f'your booking for room {booking.room_id.number}-{booking.room_id.room_type} '
                                f'at the hotel {booking.room_id.hotel_id.name} from the {booking.check_in_date} '
                                f'to the {booking.check_out_date}.',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[booking.user_id.email],
                        fail_silently=False,
                    )
            return redirect('profile')


class ListReviews(LoginRequiredMixin, UserPassesTestMixin, ListView):
    paginate_by = 5
    model = ReviewModel
    template_name = 'reservations/list_reviews.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        return ReviewModel.objects.all()

    def test_func(self):
        return self.request.user.is_superuser


class ListRelevantBookings(LoginRequiredMixin, UserPassesTestMixin, ListView):
    paginate_by = 3
    model = BookingModel
    template_name = 'reservations/list_bookings.html'
    context_object_name = 'bookings'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListRelevantBookings, self).get_context_data(**kwargs)
        context['current_date'] = datetime.now().date()
        return context

    def get_queryset(self):
        return BookingModel.objects.filter(check_out_date__gte=datetime.now().date()).order_by('room_id__hotel_id',
                                                                                               '-check_in_date')

    def test_func(self):
        return self.request.user.is_superuser


class AnalyticsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = BookingModel
    template_name = 'reservations/analytics.html'
    context_object_name = 'total_bookings'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AnalyticsView, self).get_context_data(**kwargs)
        context['hotel_bookings_count'] = BookingModel.objects.filter(deleted=False).values(
            'room_id__hotel_id__name').annotate(bookings_per_hotel=Count('id')).order_by('-bookings_per_hotel')
        context['user_hotels_rating'] = ReviewModel.objects.all().values('hotel_id__name').annotate(
            avg_rating=Round(Avg('rating'))).order_by('-avg_rating')
        return context

    def get_queryset(self):
        return BookingModel.objects.filter(deleted=False).aggregate(Count('id'))

    def test_func(self):
        return self.request.user.is_superuser
