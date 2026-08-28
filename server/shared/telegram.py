import json

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views import View

from users.models import FeedBack


class TelegramService:

    @staticmethod
    def send_message(chat_id, text):
        url = f"https://api.telegram.org/" f"bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def send_ticket_notification(feedback):
        text = (
            "🚨 NEW MOKVIO FEEDBACK\n\n"
            f"🎫 Ticket: {feedback.ticket}\n"
            f"📌 Type: {feedback.get_type_of_feedback_display()}\n"
            f"📝 Title: {feedback.title}\n\n"
            f"👤 Created by: {feedback.created_by}\n\n"
            f"💬 Description:\n{feedback.description}\n\n"
            f"🔧 Steps:\n{feedback.steps_to_reproduce}\n\n"
            f"⚠️ Actual behavior:\n{feedback.actual_behavior}\n\n"
            f"Use /ticket {feedback.ticket} to view this ticket."
        )

        for chat_id in settings.TELEGRAM_ADMIN_CHAT_IDS:
            TelegramService.send_message(
                chat_id=chat_id,
                text=text,
            )


class TelegramWebhookView(View):

    def post(self, request, *args, **kwargs):
        telegram_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

        if telegram_secret != settings.TELEGRAM_WEBHOOK_SECRET:
            return JsonResponse(
                {"detail": "Unauthorized"},
                status=403,
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"detail": "Invalid JSON"},
                status=400,
            )

        message = data.get("message")

        if not message:
            return JsonResponse({"ok": True})

        chat = message.get("chat", {})
        chat_id = chat.get("id")

        if not chat_id:
            return JsonResponse({"ok": True})

        if str(chat_id) not in settings.TELEGRAM_ADMIN_CHAT_IDS:
            return JsonResponse({"ok": True})

        text = message.get("text", "").strip()

        if text == "/start":
            self.send(
                chat_id,
                ("🤖 Mokvio Bot\n\n" "/tickets - List feedback tickets\n" "/ticket <ticket> - View ticket details"),
            )

        elif text == "/tickets":
            self.send_ticket_list(chat_id)

        elif text.startswith("/ticket "):
            ticket = text.split(" ", 1)[1].strip()
            self.send_ticket(chat_id, ticket)

        else:
            self.send(
                chat_id,
                ("Unknown command.\n\n" "/tickets\n" "/ticket <ticket>"),
            )

        return JsonResponse({"ok": True})

    def send(self, chat_id, text):
        TelegramService.send_message(
            chat_id=chat_id,
            text=text,
        )

    def send_ticket_list(self, chat_id):
        tickets = FeedBack.objects.select_related("created_by").order_by("-created_at")[:20]

        if not tickets:
            self.send(
                chat_id,
                "🎫 No feedback tickets found.",
            )
            return

        lines = ["🎫 MOKVIO TICKETS\n"]

        for feedback in tickets:
            lines.append(
                f"🎫 {feedback.ticket}\n" f"📌 {feedback.title}\n" f"🏷 {feedback.get_type_of_feedback_display()}\n"
            )

        lines.append("\nUse /ticket <ticket> to view details.")

        self.send(
            chat_id,
            "\n".join(lines),
        )

    def send_ticket(self, chat_id, ticket):
        try:
            feedback = FeedBack.objects.select_related("created_by").get(ticket=ticket)
        except FeedBack.DoesNotExist:
            self.send(
                chat_id,
                f"❌ Ticket {ticket} was not found.",
            )
            return

        text = (
            "🎫 MOKVIO TICKET\n\n"
            f"🎫 Ticket: {feedback.ticket}\n"
            f"📌 Type: {feedback.get_type_of_feedback_display()}\n"
            f"📝 Title: {feedback.title}\n\n"
            f"💬 Description:\n{feedback.description}\n\n"
            f"🔧 Steps to reproduce:\n"
            f"{feedback.steps_to_reproduce}\n\n"
            f"⚠️ Actual behavior:\n"
            f"{feedback.actual_behavior}\n\n"
            f"👤 Created by: {feedback.created_by}\n"
            f"📅 Created: {feedback.created_at}"
        )

        self.send(
            chat_id,
            text,
        )
