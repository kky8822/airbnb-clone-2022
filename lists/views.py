from django.shortcuts import render, redirect, reverse
from rooms import models as room_models
from . import models
from django.views.generic import TemplateView

# Create your views here.


def save_room(request, pk):
    room = room_models.Room.objects.get_or_none(pk=pk)
    if room is not None:
        the_list, _ = models.List.objects.get_or_create(
            user=request.user, name="My Favourites"
        )
        the_list.rooms.add(room)
    return redirect(reverse("rooms:detail", kwargs={"pk": pk}))


def remove_room(request, pk):
    room = room_models.Room.objects.get_or_none(pk=pk)
    if room is not None:
        the_list = models.List.objects.get(user=request.user, name="My Favourites")
        the_list.rooms.remove(room)
    return redirect(reverse("rooms:detail", kwargs={"pk": pk}))


class SeeFavsView(TemplateView):
    template_name = "lists/list_detail.html"
