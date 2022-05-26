from django.http import Http404
from django.db.models import Q
from django.shortcuts import redirect, reverse, render
from django.views.generic import View
from users import models as user_models
from . import models as conv_models


# Create your views here.
def go_conversation(request, h_pk, g_pk):
    host = user_models.User.objects.get_or_none(pk=h_pk)
    guest = user_models.User.objects.get_or_none(pk=g_pk)

    if host is not None and guest is not None:
        conversations = conv_models.Conversation.objects.filter(
            participants=host
        ).filter(participants=guest)
        if len(conversations) != 0:
            conversation = conversations[0]
        else:
            conversation = conv_models.Conversation.objects.create()
            conversation.participants.add(host, guest)

        return redirect(reverse("conversations:detail", kwargs={"pk": conversation.pk}))


class ConversationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        conversation = conv_models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()

        return render(
            self.request,
            "conversations/conversation_detail.html",
            {"conversation": conversation},
        )

    def post(self, *args, **kwargs):
        pk = kwargs.get("pk")

        conversation = conv_models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()
        message = self.request.POST.get("message", None)

        if message is not None:
            conv_models.Message.objects.create(
                message=message,
                user=self.request.user,
                conversation=conversation,
            )

        return redirect(reverse("conversations:detail", kwargs={"pk": pk}))
