from pytest_cases import parametrize, parametrize_with_cases

from littoral.models import Album, ApiSession, ImageSize
from littoral.request import Request
from littoral.testing import AlbumFactory, ApiSessionFactory
from tests.cases_album import AlbumCase
from tests.conftest import CompareModels


@parametrize_with_cases("test_case", cases=".cases_album")
def test_album_parsed_from_json(test_case: AlbumCase, compare_models: CompareModels):
    compare_models(Album.model_validate_json(test_case.raw), test_case.parsed)


def test_factory_produces_fake_objects():
    album = AlbumFactory().build(title="given title")

    assert isinstance(album, Album)
    assert album.title == "given title"


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
def test_cover_request_constructed_from_cover_uuid_and_size(size, url):
    session = ApiSessionFactory().build()
    request = (
        AlbumFactory().build(cover_uuid="aaa-bbb-ccc-ddd").image(size).build(session)
    )

    assert request.method == "GET"
    assert str(request.url) == url


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

    request = AlbumFactory().build(id=123).tracks(limit, offset).build(session)

    assert request.url == expected.url
    assert request.params == (
        expected.params | {"countryCode": "GB", "sessionId": "1234"}
    )
    assert request.headers == session.headers()
