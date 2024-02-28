# ruff: noqa: E501
import json
from datetime import datetime, timedelta

from littoral.auth.client_oauth2 import AuthenticatedUser, SimpleOauthFlow
from littoral.testing import OauthFlowFactory
from tests.conftest import CompareModels


def test_authenticated_user_parsed_from_json(
    compare_models: CompareModels, freeze_time: datetime
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
