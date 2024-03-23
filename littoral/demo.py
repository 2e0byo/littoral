from base64 import b64encode

import httpx
from pydantic import BaseModel, Field

from littoral.auth.models import ExpiryTime

client_id = "HKp20SxljzST0spV"
client_secret = "7m8Te1MDfWYphOTHcGz3BL1CgyVadsgstJMkx5Qjg6s="
creds = b64encode(f"{client_id}:{client_secret}".encode()).decode()

response = httpx.post(
    "https://auth.tidal.com/v1/oauth2/token",
    headers={"Authorization": f"Basic {creds}"},
    data={"grant_type": "client_credentials"},
)
response.raise_for_status()


class Token(BaseModel):
    access_token: str
    expires_at: ExpiryTime = Field(alias="expires_in")


token = Token.model_validate_json(response.read())


def headers() -> dict:
    return {
        "Authorization": f"Bearer {token.access_token}",
        "Content-Type": "application/vnd.tidal.v1+json",
    }


def params() -> dict:
    return {"countryCode": "GB"}


api_root = "https://openapi.tidal.com/"
json = """{
    "adSupportedStreamReady": true,
    "allowStreaming": true,
    "artist": {
        "id": 2935,
        "name": "Various Artists",
        "picture": null,
        "type": "MAIN"
    },
    "artists": [
        {
            "id": 2935,
            "name": "Various Artists",
            "picture": null,
            "type": "MAIN"
        }
    ],
    "audioModes": [
        "STEREO"
    ],
    "audioQuality": "LOSSLESS",
    "copyright": "© 2016 Mercury Music Group",
    "cover": "8f0b90a8-5eae-404f-b20b-005a51b5d012",
    "djReady": true,
    "duration": 3878,
    "explicit": false,
    "id": 57642369,
    "mediaMetadata": {
        "tags": [
            "LOSSLESS"
        ]
    },
    "numberOfTracks": 24,
    "numberOfVideos": 0,
    "numberOfVolumes": 1,
    "popularity": 18,
    "premiumStreamingOnly": false,
    "releaseDate": "2016-02-26",
    "stemReady": false,
    "streamReady": true,
    "streamStartDate": "2016-02-26T00:00:00.000+0000",
    "title": "Gainsbourg London Paris 1963 - 1971",
    "type": "ALBUM",
    "upc": "00600753673829",
    "url": "http://www.tidal.com/album/57642369",
    "version": null,
    "vibrantColor": "#ac590b",
    "videoCover": null
}
""".encode()
