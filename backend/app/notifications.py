from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from app.auth_store import auth_store
from app.models import Application, Notification


class EmailProvider(Protocol):
    def send(self, recipient: str, subject: str, message: str) -> None: ...


class InMemoryEmailProvider:
    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []

    def send(self, recipient: str, subject: str, message: str) -> None:
        self.sent.append(
            {"recipient": recipient, "subject": subject, "message": message}
        )


email_provider: EmailProvider = InMemoryEmailProvider()


def create_application_reminders(
    user_id: str, applications: list[Application]
) -> list[Notification]:
    reminders: list[Notification] = []
    for application in applications:
        candidates = (
            ("deadline", application.deadline, "Application deadline"),
            ("interview", application.interview_at, "Interview"),
            ("next_action", application.next_action_at, application.next_action),
        )
        for kind, due_at, label in candidates:
            if due_at is None or not label:
                continue
            record = auth_store.save_notification(
                user_id,
                {
                    "application_id": application.id,
                    "kind": kind,
                    "title": label,
                    "message": f"{label} for {application.job_title or application.job_id}.",
                    "due_at": due_at,
                },
            )
            reminders.append(Notification.model_validate(record))
    return reminders


def mark_notification(
    user_id: str, notification_id: str, read: bool
) -> Notification | None:
    notification = auth_store.notifications[user_id].get(notification_id)
    if notification is None:
        return None
    notification["read_at"] = datetime.now(UTC) if read else None
    return Notification.model_validate(notification)


def deliver_due_notifications(
    user_id: str, email: str, now: datetime | None = None
) -> list[Notification]:
    current_time = now or datetime.now(UTC)
    delivered: list[Notification] = []
    for record in auth_store.list_notifications(user_id):
        if record["delivery_status"] != "pending" or record["due_at"] > current_time:
            continue
        preferences = auth_store.notification_preferences.get(user_id, {})
        if preferences.get("email_enabled", True):
            try:
                record["attempts"] += 1
                email_provider.send(email, record["title"], record["message"])
                record["delivery_status"] = "delivered"
                record["delivered_at"] = current_time
                delivered.append(Notification.model_validate(record))
            except (OSError, RuntimeError, TimeoutError):
                record["delivery_status"] = "failed"
    return delivered
