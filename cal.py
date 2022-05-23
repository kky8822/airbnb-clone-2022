import calendar
from django.utils import timezone


class Day:
    def __init__(self, day, past, month, year):
        self.day = day
        self.month = month
        self.year = year
        self.past = past

    def __str__(self):
        return str(self.day)


class Calendar(calendar.Calendar):
    def __init__(self, year, month):

        super().__init__(firstweekday=6)

        self.year = year
        self.month = month
        self.day_names = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
        self.month_names = (
            "January",
            "Febuary",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        )

    def get_days(self):
        weeks = self.monthdays2calendar(self.year, self.month)
        days = []
        for week in weeks:
            for day, _ in week:
                now = timezone.now()
                today = now.day
                month = now.month
                past = False
                if self.month == month:
                    if day <= today:
                        past = True
                new_day = Day(day=day, past=past, month=self.month, year=self.year)
                days.append(new_day)
        return days

    def get_month(self):
        return self.month_names[self.month - 1]
