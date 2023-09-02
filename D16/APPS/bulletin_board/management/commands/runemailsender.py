import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from APPS.bulletin_board.models import Post

logger = logging.getLogger(__name__)


def my_job():
    """
    This function sends an email to a list of users containing links to the top 5 posts from the current week.
    """
    get_posts_objects = Post.objects.all().dates("datetime", "week").values()[:7]

    get_users_emails = list(User.objects.all().values_list('email', flat=True)[1:])

    for email in get_users_emails:
        send_mail(
            subject=f'Weekly posts',
            message='\n'.join(['{}... Link=http://127.0.0.1:8000/{}/'.format(
                _content["header"][:10],
                _content["id"]) for _content in get_posts_objects]),
            from_email=None,
            recipient_list=[email],
        )


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This function deletes old job executions in Django using a maximum age parameter.

    param max_age:
        The max_age parameter is an optional argument that specifies the maximum age (in seconds) of job executions
        that should be deleted.

        By default, it is set to 604,800 seconds, which is equivalent to one week.
        This means that any job execution that is older than one week will be deleted, defaults to 604_800 (optional)
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    """This is a Python class that runs APScheduler and schedules two jobs, one that runs at 09:00 on every Monday.
    and another that runs weekly to delete old job executions."""
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            # trigger=CronTrigger(second="00 9 * * 1"),  # 09:00 on every Monday
            trigger=CronTrigger(second="*/10"),  # For testing
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
