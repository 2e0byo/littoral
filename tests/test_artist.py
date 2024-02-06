import json

from littoral.models import Artist, Role
from littoral.testing import ArtistFactory

artist_response = json.dumps(
    {
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
)


def test_artist_parsed_from_json(compare_models):
    target = Artist(
        id=64643,
        name="The Black Keys",
        roles=[Role.Artist, Role.Songwriter, Role.Producer, Role.Engineer],
        picture_uuid="0ed9f0cd-fce1-4894-baf4-d50c35fc7585",
        popularity=65,
    )

    parsed = Artist.model_validate_json(artist_response)

    compare_models(parsed, target)


def test_factory_produces_fake_objects():
    artist = ArtistFactory().build(name="Arty")

    assert isinstance(artist, Artist)
    assert artist.name == "Arty"
