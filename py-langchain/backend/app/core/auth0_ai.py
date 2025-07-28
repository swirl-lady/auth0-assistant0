from auth0_ai.authorizers.types import Auth0ClientParams
from auth0_ai_langchain.auth0_ai import Auth0AI
from fastapi import Request
from langchain_core.runnables import RunnableConfig

from app.core.auth import auth_client
from app.core.config import settings

auth0_ai = Auth0AI(
    Auth0ClientParams(
        {
            "domain": settings.AUTH0_DOMAIN,
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "client_assertion_signing_alg": None,
            "client_assertion_signing_key": None,
            "telemetry": None,
            "timeout": None,
            "protocol": None,
        }
    )
)


with_calendar_free_busy_access = auth0_ai.with_federated_connection(
    connection="google-oauth2",
    scopes=["https://www.googleapis.com/auth/calendar.freebusy"],
)
