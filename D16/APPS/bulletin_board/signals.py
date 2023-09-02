from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Feedback, SubscribeFeedback


@receiver(post_save, sender=Feedback)
def feedback_created(instance, created, **kwargs):
    """
    This function sends an email notification to the user who posted a comment on a post.

    param instance:
        The instance parameter refers to the instance of the Feedback model that triggered the signal

    param created:
        A boolean value that indicates whether the instance being saved
        is a new instance or an existing one being updated

    return:
        If the `created` parameter is `False`, the function returns `None`.
        If `created` is `True`, the function sends an email to the user who posted the feedback and returns `None`.
    """
    if not created:
        return

    user_id = Feedback.objects.all().values().last()["feedback_user_id"]

    email = [User.objects.filter(id=user_id).values("email").last()["email"]]

    subject = f'Comment successfully posted in {instance.feedback_post.header} post'

    text_content = (
        f'Feedback on : {instance.feedback_post.header} post\n'
        f'Link: http://127.0.0.1:8000{instance.feedback_post.get_post_url()}'
    )
    html_content = (
        f'Feedback on : {instance.feedback_post.header} post\n'
        f'Link: http://127.0.0.1:8000{instance.feedback_post.get_post_url()}'
    )

    mail_admins(
        subject='',
        message=f'New comment in {instance.feedback_post.header} post',
    )

    for _email in email:
        msg = EmailMultiAlternatives(subject, text_content, None, [_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@receiver(post_save, sender=SubscribeFeedback)
def feedback_received(instance, created, **kwargs):
    """
    This function sends an email to the user and admins when a new feedback is received for a post.

    param instance:
        The instance of the SubscribeFeedback model that was just saved

    param created:
        A boolean value that indicates whether the instance of the SubscribeFeedback model was just created or not

    return:
        If `created` is `True`, nothing is being returned.
        If `created` is `False`, the function returns `None`.
    """
    if not created:
        return

    user_id = Feedback.objects.all().values().last()["feedback_user_id"]

    email = [User.objects.filter(id=user_id).values("email").last()["email"]]

    subject = f'Your review has been successfully received in post {instance.feedback.feedback_post.header}'

    text_content = (
        f'Successfully received feedback in post {instance.feedback.feedback_post.header}\n'
        f'Link: http://127.0.0.1:8000{instance.feedback.feedback_post.get_post_url()}'
    )
    html_content = (
        f'Successfully received feedback in post {instance.feedback.feedback_post.header}\n'
        f'Link: http://127.0.0.1:8000{instance.feedback.feedback_post.get_post_url()}'
    )

    mail_admins(
        subject='',
        message=f'Successfully received feedback for {instance.feedback.feedback_user}',
    )

    for _email in email:
        msg = EmailMultiAlternatives(subject, text_content, None, [_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
