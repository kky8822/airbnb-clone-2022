import datetime
from django import template
from reservations import models as reservation_models

register = template.Library()


@register.simple_tag
def is_booked_by_checkinout(room, day):
    if day.day == 0:
        return
    try:
        date = datetime.datetime(year=day.year, month=day.month, day=day.day)
        reservation = reservation_models.Reservation.objects.get(
            day=date, reservation__room=room
        )
        check_in = datetime.datetime(room.check_in)
        check_out = datetime.datetime(room.check_out)
        if date >= check_in and date <= check_out:
            return True
        else:
            return False
    except reservation_models.BookedDay.DoesNotExist:
        return False
