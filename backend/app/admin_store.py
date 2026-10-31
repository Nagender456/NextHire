from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.models import (
    ActivitySummary,
    AuditEvent,
    RetentionPolicy,
    RetentionPurgeResult,
)


class AdminStore:
    def __init__(self) -> None:
        self.audit_events: list[AuditEvent] = []
        self.activity_events: list[tuple[str, datetime]] = []
        self.retention = RetentionPolicy()

    def audit(
        self,
        actor_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=f"audit-{len(self.audit_events) + 1}",
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
            created_at=datetime.now(UTC),
        )
        self.audit_events.append(event)
        return event

    def activity(self, event: str) -> None:
        self.activity_events.append((event, datetime.now(UTC)))

    def summaries(self) -> list[ActivitySummary]:
        grouped: dict[str, list[datetime]] = {}
        for event, created_at in self.activity_events:
            grouped.setdefault(event, []).append(created_at)
        return [
            ActivitySummary(event=event, count=len(times), last_seen_at=max(times))
            for event, times in sorted(grouped.items())
        ]

    def purge(self) -> RetentionPurgeResult:
        now = datetime.now(UTC)
        audit_cutoff = now - timedelta(days=self.retention.audit_retention_days)
        activity_cutoff = now - timedelta(days=self.retention.activity_retention_days)
        old_audits = len(self.audit_events)
        old_activity = len(self.activity_events)
        self.audit_events[:] = [
            event for event in self.audit_events if event.created_at >= audit_cutoff
        ]
        self.activity_events[:] = [
            item for item in self.activity_events if item[1] >= activity_cutoff
        ]
        return RetentionPurgeResult(
            audit_events_removed=old_audits - len(self.audit_events),
            activity_events_removed=old_activity - len(self.activity_events),
        )


admin_store = AdminStore()
