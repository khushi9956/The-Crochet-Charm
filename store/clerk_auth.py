import os

from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions

from django.contrib.auth.models import User

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import ClerkUserProfile


class ClerkAuthentication(BaseAuthentication):

    def authenticate(self, request):
        secret_key = os.getenv("CLERK_SECRET_KEY")

        if not secret_key:
            raise AuthenticationFailed(
                "CLERK_SECRET_KEY is not configured."
            )

        try:
            clerk = Clerk(
                bearer_auth=secret_key
            )

            authorized_parties = [
                "http://localhost:3000",
                "https://the-crochet-charm-next.vercel.app",
            ]

            request_state = clerk.authenticate_request(
                request,
                AuthenticateRequestOptions(
                    authorized_parties=authorized_parties,
                ),
            )

        except Exception as exc:
            raise AuthenticationFailed(
                "Unable to authenticate with Clerk."
            ) from exc

        if not request_state.is_signed_in:
            return None

        payload = request_state.payload or {}
        clerk_user_id = payload.get("sub")

        if not clerk_user_id:
            raise AuthenticationFailed(
                "Clerk user ID was not found."
            )

        try:
            profile = ClerkUserProfile.objects.select_related(
                "user"
            ).get(
                clerk_user_id=clerk_user_id
            )

            user = profile.user

        except ClerkUserProfile.DoesNotExist:

            username = f"clerk_{clerk_user_id}"

            user, created = User.objects.get_or_create(
                username=username
            )

            ClerkUserProfile.objects.create(
                user=user,
                clerk_user_id=clerk_user_id,
            )

        return (user, request_state)