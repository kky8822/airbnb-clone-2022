from django.contrib import admin
from . import models


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    """Message Admin Definition"""

    list_display = ("__str__", "created")


class MessageInline(admin.TabularInline):
    model = models.Message


@admin.register(models.Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Conversation Admin Definition"""

    filter_horizontal = ("participants",)
    list_display = (
        "__str__",
        "count_participants",
        "count_messages",
    )

    fields = ("participants",)
    inlines = (MessageInline,)
