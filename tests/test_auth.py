import json
from datetime import datetime, timedelta

from littoral.auth import OauthFlow

# def test_now_defers_to_datetime_now(mocker):
#     mocker.patch("littoral.auth.now")


def test_oauth_flow_parsed_from_json(compare_models, mocker):
    now = datetime.now()
    mocker.patch("littoral.auth.datetime", **{"now.return_value": now})
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
    expected = OauthFlow(
        device_code="8a409920-e440-4a0f-9f53-d2d6fe166765",
        user_code="JOASE",
        verification_url="https://link.tidal.com/JOASE",
        interval=2,
        expires_at=now + timedelta(seconds=300),
    )

    parsed = OauthFlow.model_validate_json(data)

    compare_models(parsed, expected)
