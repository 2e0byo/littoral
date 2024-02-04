from polyfactory.factories.pydantic_factory import ModelFactory

from python_tidal_experimental.models import Album, Artist


class AlbumFactory(ModelFactory):
    __model__ = Album


class ArtistFactory(ModelFactory):
    __model__ = Artist
