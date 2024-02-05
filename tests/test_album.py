import json
from datetime import date, datetime, timedelta, timezone

from pytest_cases import parametrize
from python_tidal_experimental.models import Album, Artist, ImageSize, Quality
from python_tidal_experimental.testing import AlbumFactory

from tests.utils import compare_models

album_response = json.dumps(
    {
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
)


def test_album_parsed_from_json():
    target = Album(
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
    )

    parsed = Album.model_validate_json(album_response)

    compare_models(target, parsed)


@parametrize(
    "size, url",
    [
        (
            ImageSize.Thumbnail,
            "https://resources.tidal.com/images/aaa/bbb/ccc/ddd/80x80.jpg",
        ),
        (
            ImageSize.Tiny,
            "https://resources.tidal.com/images/aaa/bbb/ccc/ddd/160x160.jpg",
        ),
        (
            ImageSize.Small,
            "https://resources.tidal.com/images/aaa/bbb/ccc/ddd/320x320.jpg",
        ),
        (
            ImageSize.Medium,
            "https://resources.tidal.com/images/aaa/bbb/ccc/ddd/640x640.jpg",
        ),
        (
            ImageSize.Large,
            "https://resources.tidal.com/images/aaa/bbb/ccc/ddd/1280x1280.jpg",
        ),
    ],
)
def test_cover_urls_constructed_from_cover_uuid_and_size(size, url):
    assert AlbumFactory().build(cover_uuid="aaa-bbb-ccc-ddd").image_url(size) == url


def test_factory_produces_fake_objects():
    album = AlbumFactory().build(title="given title")

    assert isinstance(album, Album)
    assert album.title == "given title"
