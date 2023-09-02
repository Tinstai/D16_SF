from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django.core.mail import mail_admins


class CustomForm(SignupForm):
    """The `CustomForm` class extends the `SignupForm` class and adds functionality to create a new user,
    add them to a group create an associated `Author` object, and send an email notification to site administrators."""

    def save(self, request):
        user = super().save(request)

        # `user.groups.add(common_users)` is adding the user to the "common users" group. This means that the user will
        # have the permissions and access rights assigned to that group.
        common_users = Group.objects.get(name="common users")
        user.groups.add(common_users)

        mail_admins(
            subject='',
            message=f'User {user.username} registered on the site.'
        )

        return user
