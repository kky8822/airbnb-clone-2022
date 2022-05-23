from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField
from core import models as core_models
import random
from cal import Calendar


class AbstractItem(core_models.TimeStampedModel):

    """Abastract Item"""

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class RoomType(AbstractItem):
    """RoomType Model Definition"""

    class Meta:
        verbose_name = "Room Type"


class Amenity(AbstractItem):
    """AmenitesItem Model Definition"""

    class Meta:
        verbose_name_plural = "Amenities"


class Facility(AbstractItem):
    """Facility Model Definition"""

    class Meta:
        verbose_name_plural = "Facilities"


class HouseRule(AbstractItem):
    """HouseRule Model Definition"""

    class Meta:
        verbose_name = "House Rule"


class Room(core_models.TimeStampedModel):

    """Room Model definition"""

    name = models.CharField(max_length=140)
    description = models.TextField()
    country = CountryField()
    city = models.CharField(max_length=80)
    price = models.IntegerField()
    address = models.CharField(max_length=140)
    guests = models.IntegerField()
    beds = models.IntegerField()
    bedrooms = models.IntegerField()
    baths = models.IntegerField()
    check_in = models.TimeField()
    check_out = models.TimeField()
    instant_book = models.BooleanField(default=False)
    host = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="rooms"
    )
    room_type = models.ForeignKey(
        "RoomType", on_delete=models.SET_NULL, null=True, related_name="rooms"
    )
    amenities = models.ManyToManyField("Amenity", blank=True, related_name="rooms")
    facilities = models.ManyToManyField("Facility", blank=True, related_name="rooms")
    house_rules = models.ManyToManyField("HouseRule", blank=True, related_name="rooms")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.city = str.capitalize(self.city)
        super().save(*args, **kwargs)

    #    super(ModelName, self).save(*args, **kwargs) # Call the real save() method

    def total_rating(self):
        all_reviews = self.reviews.all()
        all_ratings = 0
        for review in all_reviews:
            all_ratings += review.rating_average()
        if self.reviews.count() == 0:
            return 0
        else:
            return round(all_ratings / len(all_reviews), 2)

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={"pk": self.pk})

    def first_photo(self):
        try:
            (photo,) = self.photos.all()[:1]
            return photo.file.url
        except ValueError:
            return None

    def get_next_four_photos(self):
        photos = self.photos.all()
        num_photos = photos.count()
        tg_photos = []
        if num_photos >= 5:
            photos_ind = []
            for i in range(4):
                a = random.randint(1, num_photos - 1)
                while a in photos_ind:
                    a = random.randint(1, num_photos - 1)
                photos_ind.append(a)
                tg_photos.append(photos[a])

        return tg_photos

    def get_calendars(self):
        now = timezone.now()
        this_year = now.year
        next_year = now.year
        this_month = now.month
        next_month = this_month + 1
        if this_month == 12:
            next_month = 1
            next_year = this_year + 1
        this_month_cal = Calendar(this_year, this_month)
        next_month_cal = Calendar(next_year, next_month)
        return [this_month_cal, next_month_cal]


class Photo(core_models.TimeStampedModel):
    """Photo Model Definition"""

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="room_photos")
    room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name="photos")

    def __str__(self):
        return self.caption
