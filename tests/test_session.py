# ruff: noqa: E501
from pytest_cases import parametrize_with_cases

from littoral.auth.models import AccessToken, ApiSession, RefreshToken, Session
from littoral.testing import (
    AccessTokenFactory,
    ApiSessionFactory,
    RefreshTokenFactory,
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


class TestRefreshToken:
    def test_factory_generates_fake(self):
        fake = RefreshTokenFactory().build()

        assert isinstance(fake, RefreshToken)


class TestApiSession:
    def test_factory_generates_fake(self):
        fake = ApiSessionFactory().build()

        assert isinstance(fake, ApiSession)
