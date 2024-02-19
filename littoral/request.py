"""A very basic request/response library to avoid depending on any implementation."""
from typing import TYPE_CHECKING, Any, Literal, NewType, Self

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator

if TYPE_CHECKING:  # pragma: nocover
    import httpx

HTTPMethod = Literal["GET", "PUT", "POST", "HEAD", "DELETE", "UPDATE"]


URL = NewType("URL", str)


class Request(BaseModel):
    """An http request."""

    method: HTTPMethod = "GET"
    url: AnyHttpUrl
    params: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
    data: dict[str, Any] | None = None

    def to_httpx(self) -> "httpx.Request":
        import httpx

        return httpx.Request(
            method=self.method,
            url=str(self.url),
            params=self.params,
            headers=self.headers,
            data=self.data,
        )


class Response(BaseModel):
    """An http response."""

    status_code: int
    url: AnyHttpUrl
    data: bytes
    headers: dict[str, str]

    @field_validator("headers", mode="before")
    @classmethod
    def cast_val_to_str(cls, val: dict[str, Any]) -> dict[str, str]:
        return {k: str(v) for k, v in val.items()}

    @classmethod
    def from_httpx(cls, httpx_response: "httpx.Response") -> Self:
        return cls(
            status_code=httpx_response.status_code,
            url=str(httpx_response.url),  # type: ignore
            headers=httpx_response.headers,  # type: ignore
            data=httpx_response.read(),
        )
