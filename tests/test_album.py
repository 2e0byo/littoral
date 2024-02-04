from datetime import date, datetime, timedelta, timezone

from python_tidal_experimental.models import Album, Artist, Quality

album_response = {
    "id": 110827651,
    "title": '"Let\'s Rock"',
    "duration": 2316,
    "streamReady": True,
    "adSupportedStreamReady": True,
    "djReady": True,
    "stemReady": False,
    "streamStartDate": "2019-04-25T17:00:00.000+0000",
    "allowStreaming": True,
    "premiumStreamingOnly": False,
    "numberOfTracks": 12,
    "numberOfVideos": 0,
    "numberOfVolumes": 1,
    "releaseDate": "2019-06-28",
    "copyright": "© 2019 Nonesuch Records Inc. for the United States and WEA International Inc. for the world outside the United States.",  # noqa: E501
    "type": "ALBUM",
    "version": None,
    "url": "http://www.tidal.com/album/110827651",
    "cover": "c9ecf56d-cae2-4881-91e2-aadc186fd058",
    "vibrantColor": "#e78cae",
    "videoCover": None,
    "explicit": False,
    "upc": "075597924961",
    "popularity": 39,
    "audioQuality": "HI_RES",
    "audioModes": ["STEREO"],
    "mediaMetadata": {"tags": ["LOSSLESS", "HIRES_LOSSLESS", "MQA"]},
    "artist": {
        "id": 64643,
        "name": "The Black Keys",
        "type": "MAIN",
        "picture": "0ed9f0cd-fce1-4894-baf4-d50c35fc7585",
    },
    "artists": [
        {
            "id": 64643,
            "name": "The Black Keys",
            "type": "MAIN",
            "picture": "0ed9f0cd-fce1-4894-baf4-d50c35fc7585",
        }
    ],
}


def test_album_parsed_from_json():
    assert (
        Album.from_json(album_response).model_dump()
        == Album(
            id=110827651,
            title='"Let\'s Rock"',
            duration=timedelta(seconds=2316),
            n_tracks=12,
            n_videos=0,
            n_volumes=1,
            release_date=date(2019, 6, 28),
            tidal_release_date=datetime(2019, 4, 25, 17, tzinfo=timezone.utc),
            cover_uuid="c9ecf56d-cae2-4881-91e2-aadc186fd058",
            popularity=39,
            audio_quality=Quality.HiRes,
            artist=Artist(
                id=64643,
                name="The Black Keys",
                picture_uuid="0ed9f0cd-fce1-4894-baf4-d50c35fc7585",
            ),
        ).model_dump()
    )
