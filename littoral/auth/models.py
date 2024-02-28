from datetime import datetime, timedelta, timezone
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field
from pydantic_extra_types.country import CountryAlpha2

from littoral.base import CamelModel
from littoral.request import Request, StatelessRequestBuilder

# local alias so we can mock datetime
_datetime = datetime


def to_absolute(v: float | str | datetime) -> datetime | str:
    if isinstance(v, _datetime):
        return v
    elif isinstance(v, str):
        return v
    else:
        return datetime.now(timezone.utc) + timedelta(seconds=v)


ExpiryTime = Annotated[datetime, BeforeValidator(to_absolute)]


class ClientConfig(CamelModel):
    client_id: str
    client_secret: str
    scope: str = "r_usr w_usr w_sub"


class AccessToken(BaseModel):
    access_token: str
    expires_at: ExpiryTime = Field(alias="expires_in")
    token_type: str
    scope: str

    def headers(self) -> dict[str, str]:
        return {"authorization": f"{self.token_type} {self.access_token}"}

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at


class RefreshToken(BaseModel):
    refresh_token: str

    def access_token(
        self, client: ClientConfig
    ) -> StatelessRequestBuilder[AccessToken]:
        return StatelessRequestBuilder.from_model(
            model=AccessToken,
            request=Request(
                method="POST",
                url="https://auth.tidal.com/v1/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": client.client_id,
                    "client_secret": client.client_secret,
                },
            ),
        )


class Session(CamelModel):
    """A session on the api, as sent with every request."""

    country: CountryAlpha2 = Field(alias="countryCode")
    id: str = Field(alias="sessionId")


class ApiSession(BaseModel):
    """All the state involved in maintaining a session with the api."""

    session: Session
    refresh_token: RefreshToken
    access_token: AccessToken
    client_config: ClientConfig

    def params(self) -> dict[str, str]:
        return self.session.model_dump(mode="json", by_alias=True)

    def headers(self) -> dict[str, str]:
        return self.access_token.headers()

    def new_access_token(self) -> StatelessRequestBuilder[AccessToken]:
        return self.refresh_token.access_token(self.client_config)
