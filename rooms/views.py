from django.views.generic import ListView, DetailView

from django.shortcuts import render

# from django.http import Http404
# from django.urls import reverse
# from django.shortcuts import redirect, render

from django_countries import countries
from . import models


class HomeView(ListView):
    """HomeView Definition"""

    model = models.Room
    context_object_name = "rooms"
    page_kwarg = "page"
    paginate_by = 10
    paginate_orphan = 5
    ordering = "created"


class RoomDetail(DetailView):
    """RoomDetail Definition"""

    model = models.Room


# Function Based View version
#
# def room_detail(request, pk):
#     try:
#         room = models.Room.objects.get(pk=pk)
#         return render(request, "rooms/detail.html", {"room": room})
#     except models.Room.DoesNotExist:
#         raise Http404()
#         # return redirect(reverse("core:home"))


def search(request):
    city = request.GET.get("city", "Anywhere")
    if city == "":
        city = "Anywhere"
    city = str.capitalize(city)
    country = request.GET.get("country", "KR")
    room_type = int(request.GET.get("room_type", 0))
    price = request.GET.get("price", 0)
    if price == "":
        price = 0
    else:
        price = int(price)
    guests = request.GET.get("guests", 0)
    if guests == "":
        guests = 0
    else:
        guests = int(guests)
    beds = request.GET.get("beds", 0)
    if beds == "":
        beds = 0
    else:
        beds = int(beds)
    bedrooms = request.GET.get("bedrooms", 0)
    if bedrooms == "":
        bedrooms = 0
    else:
        bedrooms = int(bedrooms)

    baths = request.GET.get("baths", 0)
    if baths == "":
        baths = 0
    else:
        baths = int(baths)

    instant = bool(request.GET.get("instant", False))
    superhost = bool(request.GET.get("superhost", False))
    s_amenities = request.GET.getlist("amenities")
    s_facilities = request.GET.getlist("facilities")

    form = {
        "city": city,
        "s_country": country,
        "s_room_type": room_type,
        "price": price,
        "guests": guests,
        "beds": beds,
        "bedrooms": bedrooms,
        "baths": baths,
        "s_amenities": s_amenities,
        "s_facilities": s_facilities,
        "instant": instant,
        "superhost": superhost,
    }

    room_types = models.RoomType.objects.all()
    amenities = models.Amenity.objects.all()
    facilities = models.Facility.objects.all()
    # house_rules = models.HouseRule.objects.all()

    choices = {
        "countries": countries,
        "room_types": room_types,
        "amenities": amenities,
        "facilities": facilities,
    }

    filter_args = {}

    if city != "Anywhere":
        filter_args["city__startswith"] = city

    filter_args["country"] = country

    if room_type != 0:
        filter_args["room_type__pk"] = room_type

    if price != 0:
        filter_args["price__lte"] = price

    if guests != 0:
        filter_args["guests__gte"] = guests

    if beds != 0:
        filter_args["beds__gte"] = beds

    if bedrooms != 0:
        filter_args["bedrooms__gte"] = bedrooms

    if baths != 0:
        filter_args["baths__gte"] = baths

    if instant:
        filter_args["instant_book"] = True

    if superhost:
        filter_args["host__superhost"] = True

    if len(s_amenities) > 0:
        for s_amenity in s_amenities:
            filter_args["amenities__pk"] = int(s_amenity)

    if len(s_facilities) > 0:
        for s_facility in s_facilities:
            filter_args["facilities__pk"] = int(s_facility)

    rooms = models.Room.objects.filter(**filter_args)

    return render(
        request,
        "rooms/search.html",
        {**form, **choices, "rooms": rooms},
    )
