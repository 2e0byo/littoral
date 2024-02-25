from pytest_cases import parametrize_with_cases

from littoral.models import Artist
from littoral.testing import ArtistFactory
from tests.cases_artist import ArtistCase
from tests.conftest import CompareModels


def test_factory_produces_fake_objects():
    artist = ArtistFactory().build(name="Arty")

    assert isinstance(artist, Artist)
    assert artist.name == "Arty"


@parametrize_with_cases("test_case", cases=".cases_artist")
def test_artist_parsed_from_json(test_case: ArtistCase, compare_models: CompareModels):
    compare_models(Artist.model_validate_json(test_case.raw), test_case.parsed)
