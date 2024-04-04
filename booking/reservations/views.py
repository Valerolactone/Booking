from datetime import datetime
from .models import BookingModel


def cancel_reservation():
    check_out_date = datetime.now().date()
    bookings = BookingModel.objects.filter(check_out_date__lt=check_out_date, cancelled=False)
    for booking in bookings:
        booking.cancelled = True
        booking.save()
