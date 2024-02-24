import json
from datetime import date, datetime, timedelta, timezone

from pytest_cases import parametrize

from littoral.models import Album, ApiSession, Artist, ImageSize, Quality
from littoral.request import Request
from littoral.testing import AlbumFactory

album_response = json.dumps(
    {
        "id": 17927863,
        "title": "Some Things (Deluxe)",
        "duration": 6712,
        "streamReady": True,
        "adSupportedStreamReady": True,
        "djReady": True,
        "stemReady": False,
        "streamStartDate": "2012-10-01T00:00:00.000+0000",
        "allowStreaming": True,
        "premiumStreamingOnly": False,
        "numberOfTracks": 22,
        "numberOfVideos": 0,
        "numberOfVolumes": 2,
        "releaseDate": "2011-09-22",
        "copyright": "Sinuz Recordings (a division of HITT bv)",
        "type": "ALBUM",
        "version": "Deluxe",
        "url": "http://www.tidal.com/album/17927863",
        "cover": "30d83a8c-1db6-439d-84b4-dbfb6f03c44c",
        "vibrantColor": "#FFFFFF",
        "videoCover": None,
        "explicit": False,
        "upc": "3610151683488",
        "popularity": 44,
        "audioQuality": "LOSSLESS",
        "audioModes": ["STEREO"],
        "mediaMetadata": {"tags": ["LOSSLESS"]},
        "artist": {
            "id": 16147,
            "name": "Lasgo",
            "type": "MAIN",
            "picture": "42b39a18-be34-4729-8dbc-acabc0e2f377",
        },
        "artists": [
            {
                "id": 16147,
                "name": "Lasgo",
                "type": "MAIN",
                "picture": "42b39a18-be34-4729-8dbc-acabc0e2f377",
            }
        ],
    }
)


def test_album_parsed_from_json(compare_models):
    target = Album(
        id=17927863,
        title="Some Things (Deluxe)",
        duration=timedelta(seconds=6712),
        n_tracks=22,
        n_videos=0,
        n_volumes=2,
        release_date=date(2011, 9, 22),
        tidal_release_date=datetime(2012, 10, 1, 0, 0, tzinfo=timezone.utc),
        cover_uuid="30d83a8c-1db6-439d-84b4-dbfb6f03c44c",
        popularity=44,
        audio_quality=Quality.Lossless,
        artist=Artist(
            id=16147,
            name="Lasgo",
            roles=None,
            picture_uuid="42b39a18-be34-4729-8dbc-acabc0e2f377",
            popularity=None,
        ),
        copyright="Sinuz Recordings (a division of HITT bv)",
        explicit=False,
        version="Deluxe",
        available=True,
        video_cover_uuid=None,
        universal_product_number=3610151683488,
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


@parametrize(
    "offset, limit, expected",
    [
        (
            0,
            10,
            Request(
                url="https://api.tidal.com/v1/albums/123/tracks",  # type: ignore
                params={"limit": 10, "offset": 0},
            ),
        ),
        (
            1,
            10,
            Request(
                url="https://api.tidal.com/v1/albums/123/tracks",  # type: ignore
                params={"limit": 10, "offset": 1},
            ),
        ),
        (
            1,
            100,
            Request(
                url="https://api.tidal.com/v1/albums/123/tracks",  # type: ignore
                params={"limit": 100, "offset": 1},
            ),
        ),
        (
            0,
            None,
            Request(
                url="https://api.tidal.com/v1/albums/123/tracks",  # type: ignore
                params={"limit": None, "offset": 0},
            ),
        ),
    ],
)
def test_track_requests_constructed_from_id_offset_and_limit(
    offset, limit, expected: Request
):
    session = ApiSession(
        country="GB",
        id=1234,
        refresh_token="refresh-token",
        access_token="access-token",
    )

    request = (
        AlbumFactory()
        .build(id=123)
        .with_session(session)
        .tracks_request(offset=offset, limit=limit)
    )

    assert request.url == expected.url
    assert request.params == (
        expected.params | {"countryCode": "GB", "sessionId": "1234"}
    )
    assert request.headers == session.headers()


def test_factory_produces_fake_objects():
    album = AlbumFactory().build(title="given title")

    assert isinstance(album, Album)
    assert album.title == "given title"
