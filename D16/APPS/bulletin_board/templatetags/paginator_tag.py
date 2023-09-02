from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    This function takes in a dictionary of keyword arguments and replaces the values of the corresponding keys in the
    current URL's query parameters.

    param context:
        The context parameter is a dictionary containing variables that are available to the template.
        It includes information about the current request, such as the user, the session,
        and the GET and POST parameters.
    return:
        URL-encoded string that includes the current query parameters of the request with any additional parameters
        specified in the function call.

        The function takes the current request context as an argument and any additional keyword arguments are
        treated as query parameters to be added or replaced in the URL.
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    return d.urlencode()
