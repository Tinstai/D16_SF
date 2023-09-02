import django_filters
from django.forms import DateTimeInput
from django_filters import DateTimeFilter
from .models import Post


class PostFilter(django_filters.FilterSet):
    """This is a Django filter class for the Post model with filters for header, category, and added_after date."""
    added_after = DateTimeFilter(
        field_name='datetime',
        lookup_expr='gt',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

    class Meta:
        model = Post

        fields = {
            'header': ['istartswith'],
            'category': ['exact'],
        }
