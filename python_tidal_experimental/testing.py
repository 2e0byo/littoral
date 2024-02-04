from polyfactory.factories.pydantic_factory import ModelFactory

from python_tidal_experimental.models import Album


class AlbumFactory(ModelFactory):
    __model__ = Album
