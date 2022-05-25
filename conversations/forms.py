from re import L
from django import forms


class AddMessageForm(forms.Form):

    message = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"placeholder": "Add a message"})
    )
