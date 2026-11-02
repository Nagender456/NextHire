from urllib.parse import urlencode
from time import time

import httpx
from fastapi import Depends, HTTPException, Request, status

from app.auth_store import auth_store
from app.config import get_settings
from app.models import Credentials, SignupRequest, User, UserRole
from app.security import generate_token, hash_password, verify_password

SESSION_COOKIE = "nexthire_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7


def signup(payload: SignupRequest) -> User:
    email = payload.email.strip().lower()
    if auth_store.find_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "EMAIL_ALREADY_REGISTERED",
                "message": "An account with this email already exists.",
            },
        )
    return auth_store.create_user(
        email, payload.display_name.strip(), hash_password(payload.password)
    )


def login(payload: Credentials) -> tuple[User, str]:
    user = auth_store.find_by_email(payload.email.strip().lower())
    password_hash = auth_store.get_password_hash(user.id) if user else None
    if (
        not user
        or not password_hash
        or not verify_password(payload.password, password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Email or password is incorrect.",
            },
        )
    token = generate_token()
    auth_store.save_session(token, user.id, time() + get_settings().session_ttl_seconds)
    return user, token


def current_user(request: Request) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    user_id = auth_store.get_session_user_id(token or "")
    user = auth_store.get_user(user_id) if user_id else None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTHENTICATION_REQUIRED",
                "message": "Sign in to access this resource.",
            },
        )
    return user


def set_session_cookie(response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        max_age=settings.session_ttl_seconds,
        path="/",
    )


def google_login_url() -> str:
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GOOGLE_OAUTH_NOT_CONFIGURED",
                "message": "Google OAuth credentials are not configured.",
            },
        )
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
    )


def github_login_url() -> str:
    settings = get_settings()
    if not settings.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GITHUB_OAUTH_NOT_CONFIGURED",
                "message": "GitHub OAuth credentials are not configured.",
            },
        )
    state = generate_token()
    auth_store.oauth_states[state] = time() + 600
    return "https://github.com/login/oauth/authorize?" + urlencode(
        {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_redirect_uri,
            "scope": "read:user user:email",
            "state": state,
        }
    )


async def github_callback(code: str, state: str) -> tuple[User, str]:
    settings = get_settings()
    expires = auth_store.oauth_states.pop(state, None)
    if not expires or expires <= time():
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_OAUTH_STATE",
                "message": "OAuth state is invalid or expired.",
            },
        )
    if not settings.github_client_id or not settings.github_client_secret:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "GITHUB_OAUTH_NOT_CONFIGURED",
                "message": "GitHub OAuth credentials are not configured.",
            },
        )
    async with httpx.AsyncClient(timeout=10) as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_redirect_uri,
            },
            headers={"Accept": "application/json"},
        )
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "GITHUB_OAUTH_FAILED",
                    "message": "GitHub authorization could not be completed.",
                },
            )
        access_token = token_response.json().get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "GITHUB_OAUTH_FAILED",
                    "message": "GitHub authorization did not return a token.",
                },
            )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }
        profile_response = await client.get(
            "https://api.github.com/user", headers=headers
        )
        emails_response = await client.get(
            "https://api.github.com/user/emails", headers=headers
        )
    if profile_response.status_code != 200 or emails_response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "GITHUB_PROFILE_FAILED",
                "message": "GitHub profile information could not be retrieved.",
            },
        )
    profile = profile_response.json()
    verified = next(
        (
            item.get("email")
            for item in emails_response.json()
            if item.get("verified") and item.get("primary")
        ),
        None,
    )
    email = (verified or profile.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "GITHUB_EMAIL_REQUIRED",
                "message": "A verified GitHub email is required.",
            },
        )
    github_id = str(profile.get("id") or "")
    user_id = auth_store.github_accounts.get(github_id)
    user = auth_store.get_user(user_id) if user_id else auth_store.find_by_email(email)
    if not user:
        user = auth_store.create_user(
            email,
            profile.get("name") or profile.get("login") or email.split("@", 1)[0],
            hash_password(generate_token()),
        )
    auth_store.github_accounts[github_id] = user.id
    auth_store.github_tokens[user.id] = access_token
    return _new_session(user)


def _new_session(user: User) -> tuple[User, str]:
    token = generate_token()
    auth_store.save_session(token, user.id, time() + get_settings().session_ttl_seconds)
    return user, token


async def google_callback(code: str) -> tuple[User, str]:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GOOGLE_OAUTH_NOT_CONFIGURED",
                "message": "Google OAuth credentials are not configured.",
            },
        )
    async with httpx.AsyncClient(timeout=10) as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "GOOGLE_OAUTH_FAILED",
                    "message": "Google authorization could not be completed.",
                },
            )
        access_token = token_response.json().get("access_token")
        profile_response = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if profile_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GOOGLE_PROFILE_FAILED",
                "message": "Google profile information could not be retrieved.",
            },
        )
    profile = profile_response.json()
    email = profile.get("email", "").strip().lower()
    if not email or not profile.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GOOGLE_EMAIL_UNVERIFIED",
                "message": "A verified Google email is required.",
            },
        )
    user = auth_store.find_by_email(email)
    if not user:
        user = auth_store.create_user(
            email,
            profile.get("name") or email.split("@", maxsplit=1)[0],
            hash_password(generate_token()),
        )
    token = generate_token()
    auth_store.sessions[token] = user.id
    return user, token


def require_user(user: User = Depends(current_user)) -> User:
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ADMIN_REQUIRED",
                "message": "Administrator access is required.",
            },
        )
    return user
