"""A very basic request/response library to avoid depending on any implementation."""
from typing import TYPE_CHECKING, Any, Literal, NewType
from urllib.parse import urlencode, urljoin

from pydantic import AnyHttpUrl, BaseModel, Field

if TYPE_CHECKING:
    import httpx

HTTPMethod = Literal["GET", "PUT", "POST", "HEAD", "DELETE", "UPDATE"]


URL = NewType("URL", str)


class Request(BaseModel):
    """An http request."""

    method: HTTPMethod = "GET"
    url: AnyHttpUrl
    params: dict[str, Any]
    headers: dict[str, str] = Field(default_factory=dict)

    def to_url(self) -> URL:
        return URL(urljoin(str(self.url), urlencode(self.params)))

    def to_httpx(self) -> "httpx.Request":
        import httpx

        return httpx.Request(
            method=self.method,
            url=str(self.url),
            params=self.params,
            headers=self.headers,
        )


class Response(BaseModel):
    """An http response."""
