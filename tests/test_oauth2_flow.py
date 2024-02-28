# ruff: noqa: E501
import json
from datetime import datetime, timedelta

from littoral.auth.client_oauth2 import AuthenticatedUser, SimpleOauthFlow, auth_request
from littoral.auth.models import ClientConfig
from littoral.request import Request
from littoral.testing import (
    AuthenticatedUserFactory,
    ClientConfigFactory,
    OauthFlowFactory,
    ResponseFactory,
    SessionFactory,
)
from tests.conftest import CompareModels


class TestAuthRequest:
    def test_makes_post_to_auth_endpoint(self, compare_models: CompareModels):
        client = ClientConfigFactory().build()

        builder = auth_request(client)
        request = builder.build()

        compare_models(
            request,
            Request(
                method="POST",
                url="https://auth.tidal.com/v1/oauth2/device_authorization",
                data={"client_id": client.client_id, "scope": client.scope},
            ),
        )

    def test_parses_to_oauth_flow(self, compare_models: CompareModels):
        flow = OauthFlowFactory().build()
        json = flow.model_dump_json(by_alias=True)
        client = ClientConfigFactory().build()
        builder = auth_request(client)

        parsed = builder.parse(ResponseFactory().build(data=json))

        assert isinstance(parsed, SimpleOauthFlow)
        compare_models(flow, parsed)


class TestOauthFlow:
    def test_parsed_from_json(
        self, compare_models: CompareModels, freeze_time: datetime
    ):
        data = json.dumps(
            {
                "deviceCode": "8a409920-e440-4a0f-9f53-d2d6fe166765",
                "userCode": "JOASE",
                "verificationUri": "link.tidal.com",
                "verificationUriComplete": "link.tidal.com/JOASE",
                "expiresIn": 300,
                "interval": 2,
            }
        ).encode()
        expected = SimpleOauthFlow(
            device_code="8a409920-e440-4a0f-9f53-d2d6fe166765",
            user_code="JOASE",
            verification_url="https://link.tidal.com/JOASE",
            interval=2,
            expires_at=freeze_time + timedelta(seconds=300),
        )

        parsed = SimpleOauthFlow.model_validate_json(data)

        compare_models(parsed, expected)

    def test_smoketest_factory(self):
        fake = OauthFlowFactory().build()

        assert isinstance(fake, SimpleOauthFlow)

    def test_user_returns_post_request_to_token_endpoint(
        self, compare_models: CompareModels
    ):
        flow = OauthFlowFactory().build(device_code="foo")
        client = ClientConfig(client_id="id", client_secret="secret", scope="scopes")

        builder = flow.user(client)
        request = builder.build()

        compare_models(
            request,
            Request(
                method="POST",
                data={
                    "client_id": "id",
                    "client_secret": "secret",
                    "scope": "scopes",
                    "device_code": "foo",
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                url="https://auth.tidal.com/v1/oauth2/token",
            ),
        )

    def test_user_parses_to_authenticated_user(self, compare_models: CompareModels):
        flow = OauthFlowFactory().build()
        client = ClientConfigFactory().build()
        expected = AuthenticatedUserFactory().build()
        json = expected.model_dump_json(by_alias=True)
        builder = flow.user(client)

        parsed = builder.parse(ResponseFactory().build(data=json))

        compare_models(parsed, expected)


class TestAuthenticatedUser:
    def test_parsed_from_json(
        self, compare_models: CompareModels, freeze_time: datetime
    ):
        raw = b'{"scope":"w_usr w_sub r_usr","user":{"userId":123,"email":"foo@bar.com","countryCode":"GB","fullName":null,"firstName":null,"lastName":null,"nickname":null,"username":"foo@bar.com","address":null,"city":null,"postalcode":null,"usState":null,"phoneNumber":null,"birthday":null,"channelId":323,"parentId":0,"acceptedEULA":true,"created":1643033404421,"updated":1683975459780,"facebookUid":0,"appleUid":null,"googleUid":null,"accountLinkCreated":false,"emailVerified":false,"newUser":false},"clientName":"Android Automotive","token_type":"Bearer","access_token":"foo_bar_access_token","refresh_token":"foo_bar_refresh_token","expires_in":604800,"user_id":1234}'
        expected = AuthenticatedUser.model_validate(
            {
                "user": {"userId": 123, "email": "foo@bar.com"},
                "token_type": "Bearer",
                "scope": "w_usr w_sub r_usr",
                "clientName": "Android Automotive",
                "access_token": "foo_bar_access_token",
                "refresh_token": "foo_bar_refresh_token",
                "expires_in": freeze_time + timedelta(seconds=604800),
                "urls": {
                    "api_v1": "https://api.tidal.com/v1",
                    "api_v2": "https://api.tidal.com/v2",
                    "oauth2": "https://auth.tidal.com/v1/oauth2/token",
                    "image": "https://resources.tidal.com/images",
                    "video": "https://resources.tidal.com/videos",
                },
            }
        )

        user = AuthenticatedUser.model_validate_json(raw)

        compare_models(user, expected)

    def test_factory_produces_fakes(self):
        fake = AuthenticatedUserFactory().build(access_token="foo")

        assert isinstance(fake, AuthenticatedUser)
        assert fake.access_token == "foo"

    def test_session_makes_get_request(self, compare_models: CompareModels):
        user = AuthenticatedUserFactory().build(access_token="foo")

        builder = user.session()
        request = builder.build()

        compare_models(
            request,
            Request(
                method="GET",
                url="https://api.tidal.com/v1/sessions",
                headers={"Authorization": f"Bearer {user.access_token}"},
            ),
        )

    def test_session_parses_to_session(self, compare_models: CompareModels):
        expected = SessionFactory().build()
        json = expected.model_dump_json(by_alias=True)
        user = AuthenticatedUserFactory().build()
        builder = user.session()

        parsed = builder.parse(ResponseFactory().build(data=json))

        compare_models(expected, parsed)
