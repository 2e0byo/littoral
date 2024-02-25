# ruff: noqa: E501
from littoral.models import Artist
from tests.models import TestCase

ArtistCase = TestCase[Artist]


def case_all_data() -> ArtistCase:
    return ArtistCase(
        raw='{"id": 64643, "name": "The Black Keys", "artistTypes": ["ARTIST", "CONTRIBUTOR"], "url": "http://www.tidal.com/artist/64643", "picture": "0ed9f0cd-fce1-4894-baf4-d50c35fc7585", "popularity": 65, "artistRoles": [{"categoryId": -1, "category": "Artist"}, {"categoryId": 2, "category": "Songwriter"}, {"categoryId": 1, "category": "Producer"}, {"categoryId": 3, "category": "Engineer"}], "mixes": {"ARTIST_MIX": "0006efdff1509a99512fe32f7e7b8d"}}'.encode(),
        parsed={
            "id": 64643,
            "name": "The Black Keys",
            "roles": ["Artist", "Songwriter", "Producer", "Engineer"],
            "picture_uuid": "0ed9f0cd-fce1-4894-baf4-d50c35fc7585",
            "popularity": 65,
        },
    )
