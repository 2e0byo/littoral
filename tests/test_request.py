import httpx
from pydantic import BaseModel

from littoral.auth.models import Session
from littoral.request import Request, RequestBuilder, Response
from littoral.testing import (
    AccessTokenFactory,
    ApiSessionFactory,
    RequestFactory,
    ResponseFactory,
)


def test_request_factory_produces_fake_objects():
    request = RequestFactory().build(url="http://example.com/foo")

    assert isinstance(request, Request)
    assert str(request.url) == "http://example.com/foo"


def test_response_factory_produces_fake_objects():
    response = ResponseFactory().build(data=b"foo bar baz")

    assert isinstance(response, Response)
    assert response.data == b"foo bar baz"


class TestRequest:
    def test_castable_to_httpx_request(self):
        constructed = httpx.Request(
            method="GET",
            url="http://example.com/",
            params=dict(foo="bar"),
            headers=dict(baz="blah"),
        )

        cast = Request(
            method="GET",
            url="http://example.com/",
            params=dict(foo="bar"),
            headers=dict(baz="blah"),
        ).to_httpx()

        assert cast.method == constructed.method
        assert cast.url == constructed.url
        assert cast.headers == constructed.headers


class TestResponse:
    def test_constructable_from_httpx_response(self, compare_models):
        httpx_response = httpx.Response(
            status_code=200,
            headers=[("foo", "bar")],
            request=httpx.Request("GET", url="http://example.com/"),
            content=b"hi",
        )
        expected = Response(
            status_code=200,
            headers={"foo": "bar", "content-length": 2},
            url="http://example.com",
            data=b"hi",
        )

        compare_models(expected, Response.from_httpx(httpx_response))


class TestRequestBuilder:
    def test_builds_request_from_api_session(self, mocker, compare_models):
        request = Request(
            method="GET",
            url="http://example.com",
            params={"foo": "bar"},
            headers={"bar": "baz"},
        )
        session = ApiSessionFactory().build(
            session=Session(countryCode="GB", sessionId="1234"),
            access_token=AccessTokenFactory.build(
                access_token="access", token_type="Bearer"
            ),
        )
        model = mocker.Mock(spec=BaseModel)
        builder = RequestBuilder.from_model(model, request)

        built = builder.build(session)

        expected = Request(
            method="GET",
            url="http://example.com",
            params={"foo": "bar", "countryCode": "GB", "sessionId": "1234"},
            headers={"authorization": "Bearer access", "bar": "baz"},
        )
        compare_models(built, expected)

    def test_parse_defers_to_model_when_built_with_model(self, mocker):
        model = mocker.Mock(spec=BaseModel)
        response = ResponseFactory().build(data=b"foo bar")
        builder = RequestBuilder.from_model(model, RequestFactory().build())

        builder.parse(response)

        model.model_validate_json.assert_called_once_with(b"foo bar")
