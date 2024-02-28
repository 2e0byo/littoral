from polyfactory.factories.pydantic_factory import ModelFactory

from littoral.auth.client_oauth2 import AuthenticatedUser, SimpleOauthFlow
from littoral.auth.models import (
    AccessToken,
    ApiSession,
    ClientConfig,
    RefreshToken,
    Session,
)
from littoral.models import Album, Artist, Urls
from littoral.request import Request, Response


class CommonMixin:
    urls = Urls.default


class AlbumFactory(ModelFactory, CommonMixin):
    __model__ = Album


class ArtistFactory(ModelFactory, CommonMixin):
    __model__ = Artist


class SessionFactory(ModelFactory):
    __model__ = Session

    @classmethod
    def country(cls) -> str:
        return cls.__random__.choice(["GB", "US"])


class RefreshTokenFactory(ModelFactory):
    __model__ = RefreshToken


class AccessTokenFactory(ModelFactory):
    __model__ = AccessToken


class ClientConfigFactory(ModelFactory):
    __model__ = ClientConfig


class ApiSessionFactory(ModelFactory, CommonMixin):
    __model__ = ApiSession

    session = SessionFactory


class OauthFlowFactory(ModelFactory):
    __model__ = SimpleOauthFlow


class AuthenticatedUserFactory(ModelFactory):
    __model__ = AuthenticatedUser


class RequestFactory(ModelFactory):
    __model__ = Request


class ResponseFactory(ModelFactory):
    __model__ = Response
