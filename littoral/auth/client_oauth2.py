from base64 import b64decode
from datetime import timedelta

from pydantic import AnyUrl, BaseModel, Field, field_validator

from littoral.auth.models import ClientConfig, ExpiryTime, Session
from littoral.base import CamelModel
from littoral.config import URLS
from littoral.models import User
from littoral.request import Request, StatelessRequestBuilder


def default_client_secret():
    """There is simply no way both to ship the secret and to hide it.

    Getting the id and token will always be trivial.  But we can obfuscate it in the
    source, which has a few minor advantages: at least the source isn't out there in the
    clear; it *might* turn away a few script kiddies, and it does make it clear that
    we're not *trying* to publish credentials.
    """
    # security by obscure variable naming!
    foobar = (
        b"VDLpi9/EY+nTNs408jVrBm+0B0sm06beDNeG1tNKTau"
        b"CoEmffJtVVXcQiW1ExkUmlNniIbuJ6ZLTVwl8"
    )
    barfoo = (
        b"AlmZx76BMa6wY75lkW0xfDryXQR3v//sa"
        b"IDyj4UPPd/mkjGtJfUHZSJU7V4mg3RV97SvEvbnp/6dEzlB"
    )
    return b64decode(
        bytes(x ^ y for x, y in zip(b64decode(barfoo), b64decode(foobar)))
    ).decode()


def default_client_id():
    foobar = b"nWZCvllnS3GjOidQUyNoUtoq5QziDx9N"
    barfoo = b"+AoXjg4iIyb1V1M6Hk06F49t3TyGTiJw"
    return b64decode(
        bytes(x ^ y for x, y in zip(b64decode(barfoo), b64decode(foobar)))
    ).decode()


android_client_config = ClientConfig(
    client_id=default_client_id(), client_secret=default_client_secret()
)


class SimpleOauthFlow(CamelModel):
    device_code: str
    user_code: str
    verification_url: AnyUrl = Field(alias="verificationUriComplete")
    expires_at: ExpiryTime = Field(alias="expiresIn")
    interval: timedelta

    @field_validator("verification_url", mode="before")
    @classmethod
    def add_scheme(cls, v: str) -> str:
        return f"https://{v}" if not v.startswith("http") else v

    def user(self, client: ClientConfig) -> StatelessRequestBuilder:
        """A request which will return the token if the user has approved the
        request."""
        return StatelessRequestBuilder.from_model(
            model=AuthenticatedUser,
            request=Request(
                method="POST",
                data=client.model_dump()
                | {
                    "device_code": self.device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                url="https://auth.tidal.com/v1/oauth2/token",
            ),
        )


def auth_request(client: ClientConfig) -> StatelessRequestBuilder[SimpleOauthFlow]:
    return StatelessRequestBuilder.from_model(
        model=SimpleOauthFlow,
        request=Request(
            method="POST",
            url="https://auth.tidal.com/v1/oauth2/device_authorization",
            data={
                "client_id": client.client_id,
                "scope": client.scope,
            },
        ),
    )


class AuthenticatedUser(BaseModel):
    user: User
    token_type: str
    scope: str
    client_name: str = Field(alias="clientName")
    access_token: str
    refresh_token: str
    expires_at: ExpiryTime = Field(alias="expires_in")

    def session(self) -> StatelessRequestBuilder:
        return StatelessRequestBuilder.from_model(
            model=Session,
            request=Request(
                method="GET",
                url=f"{URLS.api_v1}/sessions",
                headers={"Authorization": f"Bearer {self.access_token}"},
            ),
        )
