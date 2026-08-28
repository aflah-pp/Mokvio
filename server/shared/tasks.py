from celery import shared_task

from users.models import FeedBack

from .telegram import TelegramService


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_feedback_telegram_notification(self, feedback_id):
    feedback = FeedBack.objects.select_related("created_by").get(pk=feedback_id)

    TelegramService.send_ticket_notification(feedback)
