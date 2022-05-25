from django import template
from lists import models as list_models

register = template.Library()


@register.simple_tag(takes_context=True)
def is_fav(context, room):
    user = context.request.user
    the_list, _ = list_models.List.objects.get_or_create(
        user=user, name="My Favourites"
    )
    return room in the_list.rooms.all()
