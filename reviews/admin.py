from django.contrib import admin
from . import models


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    """Review Admin Definition"""

    list_display = (
        "__str__",
        "room",
        "rating_average",
    )

    search_fields = ("^room__name",)
