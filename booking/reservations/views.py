from datetime import datetime
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, UpdateView
from .forms import UpdateReservationForm
from .models import BookingModel, ReviewModel
from hotels.models import PhotoModel, RoomModel, HotelModel
from .services import get_unavailable_dates
from hotels.views import Round


class BookingInfoView(LoginRequiredMixin, UpdateView):
    model = BookingModel
    form_class = UpdateReservationForm
    template_name = 'reservations/certain_reservation.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super(BookingInfoView, self).get_context_data(**kwargs)
        context['booking'] = self.object
        context['current_date'] = datetime.now().date()
        context['price'] = (
                                       self.object.check_out_date - self.object.check_in_date).days * self.object.room_id.price_per_night
        context['unavailable_dates'] = get_unavailable_dates(self.object.room_id)
        context['photos'] = PhotoModel.objects.filter(room_id=self.object.room_id)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if request.POST.get('delete-button') and request.user.is_authenticated:
            self.object.deleted = True
            self.object.cancelled = True
            self.object.deleted_at = datetime.now()
            self.object.save()
            if request.user.is_superuser:
                @transaction.on_commit
                def send_booking_confirmation_email():
                    send_mail(
                        subject='Cancellation of Booking',
                        message=f'We are sorry to inform you, but due to the circumstances  we have to cancel '
                                f'your booking for room {self.object.room_id.number}-{self.object.room_id.room_type} '
                                f'at the hotel {self.object.room_id.hotel_id.name} from the {self.object.check_in_date} '
                                f'to the {self.object.check_out_date}.',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[self.object.user_id.email],
                        fail_silently=False,
                    )
            return redirect('profile')
        if request.POST.get('update-button') and form.is_valid():
            with transaction.atomic():
                form.save()
                return redirect('booking_info', pk=self.kwargs.get('pk'))
        else:
            return self.form_invalid(form, **kwargs)

    def form_invalid(self, form, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(
            self.get_context_data(form=form, **kwargs))


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
