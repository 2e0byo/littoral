from pytest_cases import parametrize
from python_tidal_experimental.models import Artist, Role

artist_response = {
    "id": 64643,
    "name": "The Black Keys",
    "artistTypes": ["ARTIST", "CONTRIBUTOR"],
    "url": "http://www.tidal.com/artist/64643",
    "picture": "0ed9f0cd-fce1-4894-baf4-d50c35fc7585",
    "popularity": 65,
    "artistRoles": [
        {"categoryId": -1, "category": "Artist"},
        {"categoryId": 2, "category": "Songwriter"},
        {"categoryId": 1, "category": "Producer"},
        {"categoryId": 3, "category": "Engineer"},
    ],
    "mixes": {"ARTIST_MIX": "0006efdff1509a99512fe32f7e7b8d"},
}


def test_artist_parsed_from_json():
    assert Artist.from_json(artist_response) == Artist(
        id=64643,
        name="The Black Keys",
        roles=[Role.Artist, Role.Songwriter, Role.Producer, Role.Engineer],
        picture_uuid="0ed9f0cd-fce1-4894-baf4-d50c35fc7585",
    )


@parametrize(
    "json, role",
    [
        ({"categoryId": -1, "category": "Artist"}, Role.Artist),
        ({"categoryId": 2, "category": "Songwriter"}, Role.Songwriter),
        ({"categoryId": 1, "category": "Producer"}, Role.Producer),
        ({"categoryId": 3, "category": "Engineer"}, Role.Engineer),
    ],
)
def test_role_parsed_from_json(json, role):
    assert Role.from_json(json) is role
