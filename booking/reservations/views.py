from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .forms import UpdateReservationForm
from .models import BookingModel
from hotels.models import PhotoModel, RoomModel
from .services import get_unavailable_dates


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
            return redirect('profile')
