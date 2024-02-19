from base64 import b64decode
from datetime import datetime, timedelta, timezone
from typing import Annotated, Self

from pydantic import (AnyUrl, BaseModel, BeforeValidator, Field,
                      field_serializer, field_validator)

from littoral.config import Urls
from littoral.models import MODEL_CONFIG
from littoral.request import Request

# local alias so we can mock datetime
_datetime = datetime


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


class ClientConfig(BaseModel):
    model_config = MODEL_CONFIG
    client_id: str
    client_secret: str
    scopes: tuple[str, ...] = ("r_usr", "w_usr", "w_sub")

    @classmethod
    def default(cls) -> Self:
        return cls(client_id=default_client_id(), client_secret=default_client_secret())

    @field_serializer("scopes")
    @staticmethod
    def as_str(scopes: tuple[str, ...]) -> str:
        return " ".join(scopes)


def auth_request(client: ClientConfig) -> Request:
    return Request(
        method="POST",
        url="https://auth.tidal.com/v1/oauth2/device_authorization",
        data={
            "client_id": client.client_id,
            "scope": " ".join(client.scopes),
        },
    )


def to_absolute(v: float | datetime) -> datetime:
    if isinstance(v, _datetime):
        return v
    else:
        return datetime.now(timezone.utc) + timedelta(seconds=v)


ExpiryTime = Annotated[datetime, BeforeValidator(to_absolute)]


class SimpleOauthFlow(BaseModel):
    model_config = MODEL_CONFIG
    device_code: str
    user_code: str
    verification_url: AnyUrl = Field(alias="verificationUriComplete")
    interval: int
    expires_at: ExpiryTime = Field(alias="expiresIn")
    urls: Urls = Field(default_factory=Urls.default)

    @field_validator("verification_url", mode="before")
    @classmethod
    def add_scheme(cls, v: str) -> str:
        return f"https://{v}" if not v.startswith("http") else v

    def token_request(self, client: ClientConfig) -> Request:
        """A request which will the return token if the user has approved the
        request."""
        return Request(
            method="POST",
            data=client.model_dump()
            | {
                "device_code": self.device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            url=self.urls.oauth2,
        )


class User(BaseModel):
    model_config = MODEL_CONFIG
    user_id: int
    email: str
    # Tidal has other fields, but I doubt we want them.


class AuthenticatedUser(BaseModel):
    model_config = MODEL_CONFIG
    user: User
    token_type: str
    client_name: str
    access_token: str
    refresh_token: str
    expires_at: ExpiryTime = Field(alias="expires_in")
