# ruff: noqa: E501
from datetime import datetime, timedelta

from pytest_cases import parametrize_with_cases

from littoral.auth.models import (
    AccessToken,
    ApiSession,
    ClientConfig,
    RefreshToken,
    Session,
)
from littoral.request import Request
from littoral.testing import (
    AccessTokenFactory,
    ApiSessionFactory,
    RefreshTokenFactory,
    ResponseFactory,
    SessionFactory,
)
from tests.conftest import CompareModels
from tests.models import TestCase

SessionCase = TestCase[Session]


class SessionTestCases:
    def case_all_data(self) -> SessionCase:
        return SessionCase(
            raw=b'{"sessionId":"1234-123-123-123","userId":12345,"countryCode":"GB","channelId":323,"partnerId":1,"client":{"id":475721180,"name":"184964830_184964830_Android Automotive","authorizedForOffline":false,"authorizedForOfflineDate":null}}',
            parsed=Session(country="GB", id="1234-123-123-123"),
        )


class TestSession:
    @parametrize_with_cases("test_case", cases=SessionTestCases)
    def test_parsed_from_json(
        self, test_case: SessionCase, compare_models: CompareModels
    ):
        compare_models(Session.model_validate_json(test_case.raw), test_case.parsed)

    def test_factory_generates_fake(self):
        fake = SessionFactory().build()

        assert isinstance(fake, Session)


class TestAccessToken:
    def test_factory_generates_fake(self):
        fake = AccessTokenFactory().build()

        assert isinstance(fake, AccessToken)

    def test_is_expired_compares_compares_time_with_now(self, freeze_time: datetime):
        fake = AccessTokenFactory().build(expires_in=freeze_time + timedelta(minutes=1))
        assert not fake.is_expired()

        fake = AccessTokenFactory().build(expires_in=freeze_time)
        assert fake.is_expired()


class TestRefreshToken:
    def test_factory_generates_fake(self):
        fake = RefreshTokenFactory().build()

        assert isinstance(fake, RefreshToken)

    def test_access_token_makes_post_request_to_token_endpoint(
        self, compare_models: CompareModels
    ):
        token = RefreshTokenFactory().build(refresh_token="refresh")
        client = ClientConfig(client_id="id", client_secret="secret")

        builder = token.access_token(client)
        request = builder.build()

        compare_models(
            request,
            Request(
                method="POST",
                url="https://auth.tidal.com/v1/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": "refresh",
                    "client_id": "id",
                    "client_secret": "secret",
                },
            ),
        )

    def test_access_token_parses_to_access_token(self, compare_models: CompareModels):
        expected = AccessTokenFactory().build()
        json = expected.model_dump_json(by_alias=True)
        token = RefreshTokenFactory().build(refresh_token="refresh")
        client = ClientConfig(client_id="id", client_secret="secret")
        builder = token.access_token(client)

        parsed = builder.parse(ResponseFactory().build(data=json))

        compare_models(expected, parsed)


class TestApiSession:
    def test_factory_generates_fake(self):
        fake = ApiSessionFactory().build()

        assert isinstance(fake, ApiSession)

    def test_new_access_token_defers_to_refresh_token(self, mocker):
        access_token = mocker.patch(
            "littoral.auth.models.RefreshToken.access_token",
            return_value=mocker.sentinel.builder,
        )
        api_session = ApiSessionFactory().build()
        builder = api_session.new_access_token()

        assert builder is mocker.sentinel.builder
        access_token.assert_called_once_with(api_session.client_config)
