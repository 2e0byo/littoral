import json
from datetime import datetime, timedelta

from littoral.auth.client_oauth2 import SimpleOauthFlow
from littoral.testing import OauthFlowFactory
from tests.conftest import CompareModels


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
