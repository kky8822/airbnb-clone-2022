from curses import pair_content
from django.views.generic import ListView, DetailView, View
from django.core.paginator import Paginator
from django.shortcuts import render

# from django.http import Http404
# from django.urls import reverse
# from django.shortcuts import redirect, render

from django_countries import countries
from . import models, forms


class HomeView(ListView):
    """HomeView Definition"""

    model = models.Room
    context_object_name = "rooms"
    page_kwarg = "page"
    paginate_by = 12
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


class SearchView(View):
    def get(self, request):
        country = request.GET.get("country")

        if country:
            form = forms.SearchFrom(request.GET)
            if form.is_valid():
                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                beds = form.cleaned_data.get("beds")
                bedrooms = form.cleaned_data.get("bedrooms")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")

                filter_args = {}
                if city != "Anywhere":
                    filter_args["city__startswith"] = city
                filter_args["country"] = country
                if room_type is not None:
                    filter_args["room_type"] = room_type
                if price is not None:
                    filter_args["price__lte"] = price
                if guests is not None:
                    filter_args["guests__gte"] = guests
                if beds is not None:
                    filter_args["beds__gte"] = beds
                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms
                if baths is not None:
                    filter_args["baths__gte"] = baths
                if instant_book:
                    filter_args["instant_book"] = True
                if superhost:
                    filter_args["host__superhost"] = True
                for amenity in amenities:
                    filter_args["amenities"] = amenity
                for facility in facilities:
                    filter_args["facilities"] = facility

                qs = models.Room.objects.filter(**filter_args).order_by("-created")

                paginator = Paginator(qs, 10, orphans=5)

                page = request.GET.get("page", 1)

                rooms = paginator.get_page(page)
                return render(
                    request, "rooms/search.html", {"form": form, "rooms": rooms}
                )
        else:
            form = forms.SearchFrom()

        return render(request, "rooms/search.html", {"form": form})
