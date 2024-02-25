import httpx
from pydantic import BaseModel

from littoral.models import ApiSession
from littoral.request import Request, RequestBuilder, Response
from littoral.testing import RequestFactory, ResponseFactory


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
        session = ApiSession(
            country="GB", id=1234, access_token="access", refresh_token="refresh"
        )
        model = mocker.Mock(spec=BaseModel)
        builder = RequestBuilder(model, request)

        built = builder.build(session)

        expected = Request(
            method="GET",
            url="http://example.com",
            params={"foo": "bar", "countryCode": "GB", "sessionId": "1234"},
            headers={"bar": "baz", "authorization": "access"},
        )
        compare_models(built, expected)

    def test_parse_defers_to_model(self, mocker):
        model = mocker.Mock(spec=BaseModel)
        response = ResponseFactory().build(data=b"foo bar")
        builder = RequestBuilder(model, RequestFactory().build())

        builder.parse(response)

        builder._model.model_validate_json.assert_called_once_with(b"foo bar")
