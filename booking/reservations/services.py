from datetime import timedelta, datetime
from .models import BookingModel


def get_unavailable_dates(room_id: int) -> list:
    current_date = datetime.now().date()
    bookings = BookingModel.objects.filter(room_id=room_id, check_out_date__gte=current_date)
    range_boundaries = []
    disabled_dates = []
    for booking in bookings:
        check_in = booking.check_in_date
        check_out = booking.check_out_date
        range_boundaries.append(check_in)
        range_boundaries.append(check_out)

        check_in += timedelta(days=1)

        while check_in < check_out:
            disabled_dates.append(check_in)
            check_in += timedelta(days=1)

    for date in range_boundaries:
        if range_boundaries.count(date) > 1:
            if date not in disabled_dates:
                disabled_dates.append(date)

    disabled_dates.sort()

    return disabled_dates
