import datetime
import json
from django import template
from reservations import models as reservation_models

register = template.Library()


@register.simple_tag
def is_booked_by_checkinout(room, day):
    if day.day == 0:
        return
    try:
        date = datetime.datetime(year=day.year, month=day.month, day=day.day)
        reservations = reservation_models.Reservation.objects.filter(room=room)
        for reservation in reservations:

            check_in = datetime.datetime.combine(
                reservation.check_in, datetime.datetime.min.time()
            )
            check_out = datetime.datetime.combine(
                reservation.check_out, datetime.datetime.min.time()
            )
            print(check_in, check_out, date, date >= check_in and date <= check_out)

            if date >= check_in and date <= check_out:
                return True

        return False

    except reservation_models.BookedDay.DoesNotExist:
        return False
