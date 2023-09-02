from django.core.exceptions import ValidationError
from django import forms
from .models import *


class FeedbackFilterForm(forms.Form):
    """This is a Django form class with a single field for searching by post name."""
    header = forms.CharField(label="Search by post name")


class PostForm(forms.ModelForm):
    """The `PostForm` class is a form that allows users to create a new post with an image, category, header, and text,
    and includes a validation check to ensure that the text is at least 150 characters long."""

    class Meta:
        model = Post
        fields = ['image',
                  'category',
                  'header',
                  'text']

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text")

        if text is not None and len(text) < 150:
            raise ValidationError(
                "The text cannot be less than 150 characters."
            )

        return cleaned_data


class FeedbackForm(forms.ModelForm):
    """The FeedbackForm class is a form that allows users to submit feedback."""

    class Meta:
        model = Feedback
        fields = ['text', ]
