from dataclasses import dataclass, field
from pathlib import Path

from httpx import Client, HTTPStatusError
from structlog import get_logger
from typing_extensions import Self

import littoral.auth.client_oauth2 as oauth2
from littoral.auth.models import AccessToken, ApiSession, ClientConfig, RefreshToken
from littoral.request import (
    ModelT,
    Request,
    RequestBuilder,
    Response,
    StatelessRequestBuilder,
)

logger = get_logger()


@dataclass
class HttpSession:
    client: Client = field(default_factory=Client)
    max_attempts: int = 3

    def send(self, request_builder: StatelessRequestBuilder[ModelT]) -> ModelT:
        request = request_builder.build()
        return self.send_request(request, request_builder)

    def send_request(self, request: Request, builder: RequestBuilder[ModelT]) -> ModelT:
        for attempt in range(self.max_attempts):
            logger.debug("Sending request", attempt=attempt, request=request)
            resp = self.client.send(request.to_httpx())
            status_code = resp.status_code
            if status_code == 404:
                raise KeyError
            elif 200 <= status_code <= 299:
                return builder.parse(Response.from_httpx(resp))
            else:
                resp.raise_for_status()

        assert False, "Unreachable"


@dataclass
class Session:
    api_session: ApiSession
    http_session: HttpSession

    @classmethod
    def login_oauth_simple(
        cls, client_config: ClientConfig = oauth2.android_client_config
    ) -> Self:
        http_session = HttpSession()
        flow = http_session.send(oauth2.auth_request(client_config))
        print(  # noqa: T201
            f"Visit {flow.verification_url} to log in.  "
            "Link expires at {flow.expires_at}."
        )
        input("Press enter when approved")
        user_auth = http_session.send(flow.user(client_config))
        session = http_session.send(user_auth.session())
        api_session = ApiSession(
            session=session,
            refresh_token=RefreshToken.model_validate(user_auth.model_dump()),
            access_token=AccessToken.model_validate(
                user_auth.model_dump(by_alias=True)
            ),
            client_config=client_config,
        )

        return cls(
            api_session=api_session,
            http_session=http_session,
        )

    @classmethod
    def from_api_session(cls, api_session: ApiSession) -> Self:
        http_session = HttpSession()
        session = cls(api_session, http_session)
        if api_session.access_token.is_expired():
            session._refresh_access_token()

        return session

    def dump_to_file(self, file: Path) -> None:
        file.write_text(self.api_session.model_dump_json(by_alias=True))

    @classmethod
    def from_file(cls, file: Path) -> Self:
        api_session = ApiSession.model_validate_json(file.read_bytes())
        return cls.from_api_session(api_session)

    def _refresh_access_token(self) -> None:
        access_token = self.http_session.send(self.api_session.new_access_token())
        self.api_session.access_token = access_token

    def send(self, request_builder: RequestBuilder[ModelT]) -> ModelT:
        request = request_builder.build(self.api_session)
        if self.api_session.access_token.is_expired():
            self._refresh_access_token()

        try:
            return self.http_session.send_request(request, request_builder)
        except HTTPStatusError as e:
            if e.response.status_code == 401:
                self._refresh_access_token()
                return self.http_session.send_request(request, request_builder)
            else:
                raise
