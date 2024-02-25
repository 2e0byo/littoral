from polyfactory.factories.pydantic_factory import ModelFactory

from littoral.auth import SimpleOauthFlow
from littoral.models import Album, ApiSession, Artist, Urls
from littoral.request import Request


class CommonMixin:
    urls = Urls.default


class AlbumFactory(ModelFactory, CommonMixin):
    __model__ = Album


class ArtistFactory(ModelFactory, CommonMixin):
    __model__ = Artist


class ApiSessionFactory(ModelFactory, CommonMixin):
    __model__ = ApiSession

    @classmethod
    def country(cls) -> str:
        return cls.__random__.choice(["GB", "US"])


class OauthFlowFactory(ModelFactory):
    __model__ = SimpleOauthFlow


class RequestFactory(ModelFactory):
    __model__ = Request
