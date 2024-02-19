import httpx

from littoral.request import Request, Response


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
