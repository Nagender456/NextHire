from typing import Protocol

from pymongo import MongoClient

from app.config import get_settings
from app.models import Application, ApplicationStatus, CareerProfile, Job, User


class Repository(Protocol):
    def get_profile(self) -> CareerProfile: ...

    def list_jobs(self) -> list[Job]: ...

    def list_applications(self) -> list[Application]: ...


class InMemoryRepository:
    """Deterministic repository for local UI development and tests."""

    def __init__(self) -> None:
        self.user = User(
            id="demo-user",
            email="demo@nexthire.local",
            display_name="Demo Candidate",
        )
        self.profile = CareerProfile(user_id=self.user.id)
        self.jobs: list[Job] = []
        self.applications: list[Application] = []

    def get_profile(self) -> CareerProfile:
        return self.profile

    def list_jobs(self) -> list[Job]:
        return self.jobs

    def list_applications(self) -> list[Application]:
        return self.applications

    def get_job(self, job_id: str) -> Job | None:
        return next((job for job in self.jobs if job.id == job_id), None)

    def add_application(self, application: Application) -> Application:
        for idx, a in enumerate(self.applications):
            if a.id == application.id:
                self.applications[idx] = application
                return application
        self.applications.append(application)
        return application

    def update_application(
        self,
        application_id: str,
        status: ApplicationStatus | None,
        resume_version_id: str | None = None,
    ) -> Application | None:
        application = next(
            (item for item in self.applications if item.id == application_id), None
        )
        if application is None:
            return None
        if status is not None:
            application.status = status
        if resume_version_id is not None:
            application.resume_version_id = resume_version_id
        return application

    def delete_application(self, application_id: str) -> bool:
        initial = len(self.applications)
        self.applications = [
            item for item in self.applications if item.id != application_id
        ]
        return len(self.applications) < initial


class MongoRepository:
    """Mongo-backed repository for the foundation entities."""

    def __init__(self, client: MongoClient) -> None:
        settings = get_settings()
        self.database = client[settings.mongodb_database]

    @property
    def applications(self) -> list[Application]:
        return self.list_applications()

    def get_profile(self) -> CareerProfile:
        document = self.database.profiles.find_one({"user_id": "demo-user"})
        return CareerProfile.model_validate(document or {"user_id": "demo-user"})

    def list_jobs(self) -> list[Job]:
        jobs = []
        for document in self.database.jobs.find():
            if "id" not in document and "_id" in document:
                document["id"] = str(document["_id"])
            jobs.append(Job.model_validate(document))
        return jobs

    def list_applications(self) -> list[Application]:
        apps = []
        for document in self.database.applications.find():
            if "id" not in document and "_id" in document:
                document["id"] = str(document["_id"])
            apps.append(Application.model_validate(document))
        return apps

    def get_job(self, job_id: str) -> Job | None:
        document = self.database.jobs.find_one(
            {"$or": [{"id": job_id}, {"_id": job_id}]}
        )
        if not document:
            return None
        if "id" not in document and "_id" in document:
            document["id"] = str(document["_id"])
        return Job.model_validate(document)

    def add_application(self, application: Application) -> Application:
        data = application.model_dump(mode="json")
        self.database.applications.update_one(
            {"id": application.id}, {"$set": data}, upsert=True
        )
        return application

    def update_application(
        self,
        application_id: str,
        status: ApplicationStatus | None,
        resume_version_id: str | None = None,
    ) -> Application | None:
        document = self.database.applications.find_one(
            {"$or": [{"id": application_id}, {"_id": application_id}]}
        )
        if not document:
            return None
        if "id" not in document and "_id" in document:
            document["id"] = str(document["_id"])
        app_obj = Application.model_validate(document)
        if status is not None:
            app_obj.status = status
        if resume_version_id is not None:
            app_obj.resume_version_id = resume_version_id
        self.database.applications.update_one(
            {"id": application_id}, {"$set": app_obj.model_dump(mode="json")}
        )
        return app_obj

    def delete_application(self, application_id: str) -> bool:
        res = self.database.applications.delete_one(
            {"$or": [{"id": application_id}, {"_id": application_id}]}
        )
        return res.deleted_count > 0


def create_repository() -> Repository:
    settings = get_settings()
    if settings.repository_backend == "mongo":
        return MongoRepository(MongoClient(settings.mongodb_url))
    return InMemoryRepository()


repository = create_repository()
