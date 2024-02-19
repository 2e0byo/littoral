from polyfactory.factories.pydantic_factory import ModelFactory

from littoral.auth import SimpleOauthFlow
from littoral.models import Album, Artist, Session, Urls


class CommonMixin:
    urls = Urls.default


class AlbumFactory(ModelFactory, CommonMixin):
    __model__ = Album


class ArtistFactory(ModelFactory, CommonMixin):
    __model__ = Artist


class SessionFactory(ModelFactory, CommonMixin):
    __model__ = Session


class OauthFlowFactory(ModelFactory):
    __model__ = SimpleOauthFlow
