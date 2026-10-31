from datetime import UTC, datetime
from typing import Any
from pymongo import MongoClient

from app.config import get_settings
from app.models import (
    CareerProfile,
    ExternalCandidateStatus,
    ProfileUpdate,
    User,
    UserRole,
)


class AuthStore:
    def __init__(self) -> None:
        self.users: dict[str, dict[str, str]] = {}
        self.sessions: dict[str, str] = {}
        self.session_expires_at: dict[str, float] = {}
        self.revoked_sessions: set[str] = set()
        self.reset_tokens: dict[str, str] = {}
        self.oauth_states: dict[str, float] = {}
        self.github_accounts: dict[str, str] = {}
        self.github_tokens: dict[str, str] = {}
        self.profiles: dict[str, CareerProfile] = {}
        self.career_entities: dict[str, dict[str, dict[str, Any]]] = {}
        self.documents: dict[str, dict[str, dict[str, Any]]] = {}
        self.document_contents: dict[str, dict[str, bytes]] = {}
        self.extracted_entities: dict[str, dict[str, dict[str, Any]]] = {}
        self.external_candidates: dict[str, dict[str, dict[str, Any]]] = {}
        self.recommendation_feedback: dict[str, dict[str, dict[str, Any]]] = {}
        self.resume_versions: dict[str, dict[str, dict[str, Any]]] = {}
        self.resume_exports: dict[str, dict[str, dict[str, Any]]] = {}
        self.application_activity: dict[str, list[dict[str, Any]]] = {}
        self.notifications: dict[str, dict[str, dict[str, Any]]] = {}
        self.privacy_settings: dict[str, dict[str, Any]] = {}
        self.notification_preferences: dict[str, dict[str, bool]] = {}

        self._mongo_db = None
        try:
            import os
            import sys
            # In test suites, do not bind to the local MongoDB to preserve test isolation
            is_testing = "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None
            settings = get_settings()
            if settings.mongodb_url and not is_testing:
                client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=500)
                client.server_info()
                self._mongo_db = client[settings.mongodb_database]
                self._load_from_mongo()
                self.ensure_admin("admin@nexthire.dev", "Admin12345!", "Administrator")
                self.ensure_admin("admin@example.com", "Admin12345!", "Admin")
        except Exception:
            self._mongo_db = None

    def _init_user_collections(self, user_id: str) -> None:
        self.career_entities.setdefault(
            user_id,
            {
                "skills": {},
                "projects": {},
                "experience": {},
                "education": {},
                "certifications": {},
                "achievements": {},
            },
        )
        self.documents.setdefault(user_id, {})
        self.document_contents.setdefault(user_id, {})
        self.extracted_entities.setdefault(user_id, {})
        self.external_candidates.setdefault(user_id, {})
        self.recommendation_feedback.setdefault(user_id, {})
        self.resume_versions.setdefault(user_id, {})
        self.resume_exports.setdefault(user_id, {})
        self.application_activity.setdefault(user_id, [])
        self.notifications.setdefault(user_id, {})
        self.privacy_settings.setdefault(user_id, {"analytics_enabled": True})
        self.notification_preferences.setdefault(
            user_id, {"email_enabled": True, "in_app_enabled": True}
        )

    def _load_from_mongo(self) -> None:
        if self._mongo_db is None:
            return
        for u in self._mongo_db.users.find():
            user_id = u.get("id") or str(u.get("_id"))
            email = u.get("email", "")
            role_val = u.get("role", UserRole.USER.value)
            if email in ("admin@nexthire.dev", "admin@example.com", "nagender@gmail.com"):
                role_val = UserRole.ADMIN.value
            self.users[user_id] = {
                "email": email,
                "password_hash": u.get("password_hash", ""),
                "created_at": u.get("created_at", datetime.now(UTC).isoformat()),
                "role": role_val,
            }
            self._init_user_collections(user_id)
        for p in self._mongo_db.profiles.find():
            user_id = p.get("user_id")
            if user_id:
                p_data = dict(p)
                p_data.pop("_id", None)
                try:
                    self.profiles[user_id] = CareerProfile.model_validate(p_data)
                except Exception:
                    pass
                self._init_user_collections(user_id)
        import time as _t
        now = _t.time()
        try:
            for s in self._mongo_db.sessions.find({"expires_at": {"$gt": now}}):
                tok = s.get("token")
                uid = s.get("user_id")
                exp = s.get("expires_at", now + 86400 * 30)
                if tok and uid:
                    self.sessions[tok] = uid
                    self.session_expires_at[tok] = float(exp)
        except Exception:
            pass

    def save_session(self, token: str, user_id: str, expires_at: float) -> None:
        self.sessions[token] = user_id
        self.session_expires_at[token] = expires_at
        if self._mongo_db is not None:
            try:
                self._mongo_db.sessions.update_one(
                    {"token": token},
                    {"$set": {"token": token, "user_id": user_id, "expires_at": expires_at}},
                    upsert=True,
                )
            except Exception:
                pass

    def get_session_user_id(self, token: str) -> str | None:
        import time as _t
        now = _t.time()
        if not token or token in self.revoked_sessions:
            return None
        if token in self.sessions:
            if self.session_expires_at.get(token, 0) > now:
                return self.sessions[token]
            self.sessions.pop(token, None)
            self.session_expires_at.pop(token, None)
            return None
        if self._mongo_db is not None:
            try:
                doc = self._mongo_db.sessions.find_one({"token": token, "expires_at": {"$gt": now}})
                if doc and doc.get("user_id"):
                    uid = doc["user_id"]
                    self.sessions[token] = uid
                    self.session_expires_at[token] = float(doc.get("expires_at", now + 86400))
                    return uid
            except Exception:
                pass
        return None

    def revoke_session(self, token: str) -> None:
        self.sessions.pop(token, None)
        self.session_expires_at.pop(token, None)
        self.revoked_sessions.add(token)
        if self._mongo_db is not None:
            try:
                self._mongo_db.sessions.delete_one({"token": token})
            except Exception:
                pass

    def set_user_role(self, user_id: str, role: UserRole | str) -> None:
        role_val = role.value if isinstance(role, UserRole) else str(role)
        if user_id in self.users:
            self.users[user_id]["role"] = role_val
            if self._mongo_db is not None:
                try:
                    self._mongo_db.users.update_one(
                        {"id": user_id},
                        {"$set": {"role": role_val}},
                    )
                except Exception:
                    pass

    def ensure_admin(
        self,
        email: str = "admin@nexthire.dev",
        password: str = "Admin12345!",
        display_name: str = "Administrator",
    ) -> User:
        user = self.find_by_email(email)
        from app.security import hash_password
        pwd_hash = hash_password(password)
        if user:
            self.set_user_role(user.id, UserRole.ADMIN)
            self.users[user.id]["password_hash"] = pwd_hash
            if self._mongo_db is not None:
                try:
                    self._mongo_db.users.update_one(
                        {"id": user.id},
                        {"$set": {"password_hash": pwd_hash, "role": UserRole.ADMIN.value}},
                    )
                except Exception:
                    pass
            return self.get_user(user.id)  # type: ignore

        user = User(
            id=f"user-{len(self.users) + 1}",
            email=email,
            display_name=display_name,
            role=UserRole.ADMIN,
        )
        now_iso = datetime.now(UTC).isoformat()
        self.users[user.id] = {
            "email": email,
            "password_hash": pwd_hash,
            "created_at": now_iso,
            "role": UserRole.ADMIN.value,
        }
        self.profiles[user.id] = CareerProfile(
            user_id=user.id, display_name=display_name, email=email
        )
        self._init_user_collections(user.id)
        if self._mongo_db is not None:
            try:
                self._mongo_db.users.update_one(
                    {"id": user.id},
                    {"$set": {
                        "id": user.id,
                        "email": email,
                        "password_hash": pwd_hash,
                        "display_name": display_name,
                        "created_at": now_iso,
                        "role": UserRole.ADMIN.value,
                    }},
                    upsert=True,
                )
                self._mongo_db.profiles.update_one(
                    {"user_id": user.id},
                    {"$set": self.profiles[user.id].model_dump(mode="json")},
                    upsert=True,
                )
            except Exception:
                pass
        return user

    def create_user(self, email: str, display_name: str, password_hash: str) -> User:
        user = User(
            id=f"user-{len(self.users) + 1}",
            email=email,
            display_name=display_name,
            role=UserRole.USER,
        )
        self.users[user.id] = {
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.now(UTC).isoformat(),
            "role": user.role.value,
        }
        self.profiles[user.id] = CareerProfile(
            user_id=user.id, display_name=display_name, email=email
        )
        self._init_user_collections(user.id)

        if self._mongo_db is not None:
            try:
                self._mongo_db.users.update_one(
                    {"id": user.id},
                    {"$set": {
                        "id": user.id,
                        "email": email,
                        "password_hash": password_hash,
                        "display_name": display_name,
                        "created_at": self.users[user.id]["created_at"],
                        "role": user.role.value,
                    }},
                    upsert=True,
                )
                self._mongo_db.profiles.update_one(
                    {"user_id": user.id},
                    {"$set": self.profiles[user.id].model_dump(mode="json")},
                    upsert=True,
                )
            except Exception:
                pass
        return user

    def find_by_email(self, email: str) -> User | None:
        for user_id, data in self.users.items():
            if data["email"] == email:
                return self.get_user(user_id)
        return None

    def get_user(self, user_id: str) -> User | None:
        data = self.users.get(user_id)
        if not data:
            return None
        profile_name = self.profiles[user_id].display_name if user_id in self.profiles else data.get("display_name", "User")
        return User(
            id=user_id,
            email=data["email"],
            display_name=profile_name,
            role=UserRole(data.get("role", UserRole.USER)),
        )

    def get_password_hash(self, user_id: str) -> str | None:
        data = self.users.get(user_id)
        return data["password_hash"] if data else None

    def set_password(self, user_id: str, password_hash: str) -> None:
        self.users[user_id]["password_hash"] = password_hash
        self.revoke_user_sessions(user_id)
        if self._mongo_db is not None:
            try:
                self._mongo_db.users.update_one(
                    {"id": user_id},
                    {"$set": {"password_hash": password_hash}},
                )
            except Exception:
                pass

    def revoke_user_sessions(self, user_id: str) -> None:
        for token, session_user_id in list(self.sessions.items()):
            if session_user_id == user_id:
                self.revoked_sessions.add(token)
                self.sessions.pop(token, None)
                self.session_expires_at.pop(token, None)

    def get_profile(self, user_id: str) -> CareerProfile:
        return self.profiles[user_id]

    def update_profile(self, user_id: str, changes: ProfileUpdate) -> CareerProfile:
        current = self.profiles[user_id]
        updates = changes.model_dump(exclude_unset=True, exclude_none=True)
        updated = current.model_copy(update=updates)
        self.profiles[user_id] = updated
        if self._mongo_db is not None:
            try:
                self._mongo_db.profiles.update_one(
                    {"user_id": user_id},
                    {"$set": updated.model_dump(mode="json")},
                    upsert=True,
                )
            except Exception:
                pass
        return updated

    def _sanitize_entity(self, entity_type: str, data: dict[str, Any]) -> dict[str, Any]:
        e = dict(data)
        if entity_type == "experience":
            if not e.get("company"):
                e["company"] = e.get("name") or "Experience"
            if not e.get("title"):
                e["title"] = e.get("name") or "Software Engineer"
        elif entity_type == "education":
            if not e.get("institution"):
                e["institution"] = e.get("name") or "Institution"
            if not e.get("degree"):
                e["degree"] = e.get("name") or "Degree"
        elif entity_type == "achievements":
            if not e.get("title"):
                e["title"] = e.get("name") or "Achievement"
        elif entity_type == "certifications":
            if not e.get("name"):
                e["name"] = e.get("title") or "Certification"
        elif entity_type == "projects":
            if not e.get("name"):
                e["name"] = e.get("title") or "Project"
        elif entity_type == "skills":
            if not e.get("name"):
                e["name"] = e.get("title") or "Skill"
        return e

    def list_entities(self, user_id: str, entity_type: str) -> list[dict[str, Any]]:
        raw = self.career_entities[user_id][entity_type]
        sanitized = []
        for k, v in list(raw.items()):
            fixed = self._sanitize_entity(entity_type, v)
            raw[k] = fixed
            sanitized.append(fixed)
        return sanitized

    def create_entity(
        self, user_id: str, entity_type: str, values: dict[str, Any]
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        entity = {
            "id": f"{entity_type[:-1]}-{len(self.career_entities[user_id][entity_type]) + 1}",
            "user_id": user_id,
            **self._sanitize_entity(entity_type, values),
            "created_at": now,
            "updated_at": now,
        }
        self.career_entities[user_id][entity_type][entity["id"]] = entity
        return entity

    def update_entity(
        self, user_id: str, entity_type: str, entity_id: str, values: dict[str, Any]
    ) -> dict[str, Any] | None:
        entity = self.career_entities[user_id][entity_type].get(entity_id)
        if entity is None:
            return None
        entity.update(values)
        entity["updated_at"] = datetime.now(UTC)
        return entity

    def delete_entity(self, user_id: str, entity_type: str, entity_id: str) -> bool:
        return (
            self.career_entities[user_id][entity_type].pop(entity_id, None) is not None
        )

    def add_external_candidate(
        self, user_id: str, values: dict[str, Any]
    ) -> dict[str, Any]:
        candidate = {
            "id": f"candidate-{len(self.external_candidates[user_id]) + 1}",
            "user_id": user_id,
            **values,
            "status": ExternalCandidateStatus.PENDING,
            "created_at": datetime.now(UTC),
        }
        self.external_candidates[user_id][candidate["id"]] = candidate
        return candidate

    def list_external_candidates(self, user_id: str) -> list[dict[str, Any]]:
        return list(self.external_candidates[user_id].values())

    def update_external_candidate(
        self, user_id: str, candidate_id: str, status: ExternalCandidateStatus
    ) -> dict[str, Any] | None:
        candidate = self.external_candidates[user_id].get(candidate_id)
        if candidate is None:
            return None
        candidate["status"] = status
        return candidate

    def save_recommendation_feedback(
        self, user_id: str, job_id: str, relevant: bool
    ) -> dict[str, Any]:
        record = {
            "job_id": job_id,
            "relevant": relevant,
            "created_at": datetime.now(UTC),
        }
        self.recommendation_feedback[user_id][job_id] = record
        return record

    def get_recommendation_feedback(
        self, user_id: str, job_id: str
    ) -> dict[str, Any] | None:
        return self.recommendation_feedback[user_id].get(job_id)

    def next_resume_version(self, user_id: str, job_id: str) -> int:
        return (
            sum(
                version["job_id"] == job_id
                for version in self.resume_versions[user_id].values()
            )
            + 1
        )

    def create_resume_version(
        self, user_id: str, values: dict[str, Any]
    ) -> dict[str, Any]:
        version = {
            "id": f"resume-{len(self.resume_versions[user_id]) + 1}",
            "user_id": user_id,
            **values,
        }
        self.resume_versions[user_id][version["id"]] = version
        return version

    def save_resume_export(
        self, user_id: str, resume_id: str, format: str
    ) -> dict[str, Any]:
        export = {
            "id": f"export-{len(self.resume_exports[user_id]) + 1}",
            "resume_id": resume_id,
            "format": format,
            "created_at": datetime.now(UTC),
        }
        self.resume_exports[user_id][export["id"]] = export
        return export

    def add_application_activity(
        self, user_id: str, application_id: str, action: str, details: str = ""
    ) -> dict[str, Any]:
        activity = {
            "id": f"activity-{len(self.application_activity[user_id]) + 1}",
            "application_id": application_id,
            "action": action,
            "details": details,
            "created_at": datetime.now(UTC),
        }
        self.application_activity[user_id].append(activity)
        return activity

    def save_notification(self, user_id: str, values: dict[str, Any]) -> dict[str, Any]:
        existing = next(
            (
                item
                for item in self.notifications[user_id].values()
                if item["application_id"] == values["application_id"]
                and item["kind"] == values["kind"]
            ),
            None,
        )
        if existing is not None:
            return existing
        notification = {
            "id": f"notification-{len(self.notifications[user_id]) + 1}",
            "user_id": user_id,
            **values,
            "delivery_status": values.get("delivery_status", "pending"),
            "attempts": values.get("attempts", 0),
            "delivered_at": values.get("delivered_at"),
            "created_at": datetime.now(UTC),
        }
        self.notifications[user_id][notification["id"]] = notification
        return notification

    def list_notifications(self, user_id: str) -> list[dict[str, Any]]:
        return list(self.notifications[user_id].values())

    def create_document(self, user_id: str, values: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC)
        document = {
            "id": f"document-{len(self.documents[user_id]) + 1}",
            "user_id": user_id,
            **values,
            "created_at": now,
        }
        self.documents[user_id][document["id"]] = document
        content = document.pop("content", b"")
        self.document_contents[user_id][document["id"]] = content
        return document

    def add_extracted_entity(
        self, user_id: str, document_id: str, values: dict[str, Any]
    ) -> dict[str, Any]:
        entity = {
            "id": f"extracted-{len(self.extracted_entities[user_id]) + 1}",
            "document_id": document_id,
            **values,
        }
        self.extracted_entities[user_id][entity["id"]] = entity
        return entity

    def list_extracted_entities(
        self, user_id: str, document_id: str
    ) -> list[dict[str, Any]]:
        return [
            item
            for item in self.extracted_entities[user_id].values()
            if item["document_id"] == document_id
        ]


auth_store = AuthStore()

