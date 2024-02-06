import httpx
from littoral.request import Request


def test_castable_to_httpx_request():
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
