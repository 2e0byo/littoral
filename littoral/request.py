"""A very basic request/response library to avoid depending on any implementation."""
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Literal,
    NewType,
    Self,
    TypeVar,
)

from pydantic import AnyHttpUrl, BaseModel, Field, TypeAdapter, field_validator

if TYPE_CHECKING:  # pragma: nocover
    import httpx

    from littoral.auth.models import ApiSession

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


T = TypeVar("T")
ModelT = TypeVar("ModelT", bound=BaseModel)


class RequestBuilder(Generic[T]):
    def __init__(self, parser: Callable[[bytes], T], request: Request) -> None:
        self._parser = parser
        self._request = request

    @classmethod
    def from_model(
        cls, model: type[ModelT], request: Request
    ) -> "RequestBuilder[ModelT]":
        """Convenience method to construct from a pydantic model."""
        return RequestBuilder(model.model_validate_json, request)

    @classmethod
    def from_adapter(
        cls, adapter: TypeAdapter[T], request: Request
    ) -> "RequestBuilder[T]":
        """Convenience method to construct from a type adapter."""
        return cls(adapter.validate_json, request)

    def build(self, session: "ApiSession") -> Request:
        """Build this request with the given token."""
        return self._request.model_copy(
            update={
                "params": session.params() | self._request.params,
                "headers": session.headers() | self._request.headers,
            }
        )

    def parse(self, response: Response) -> T:
        """Parse the server's response to the correct model."""
        return self._parser(response.data)
        return (
            self._parser.validate_json(response.data)
            if isinstance(self._parser, TypeAdapter)
            else self._parser.model_validate_json(response.data)
        )


class StatelessRequestBuilder(RequestBuilder, Generic[T]):
    """A request builder whose request is already built."""

    @classmethod
    def from_model(
        cls, model: type[ModelT], request: Request
    ) -> "StatelessRequestBuilder[ModelT]":
        """Convenience method to construct from a pydantic model."""
        return StatelessRequestBuilder(model.model_validate_json, request)

    @classmethod
    def from_adapter(
        cls, adapter: TypeAdapter[T], request: Request
    ) -> "StatelessRequestBuilder[T]":
        """Convenience method to construct from a type adapter."""
        return StatelessRequestBuilder(adapter.validate_json, request)

    def build(self, *_) -> Request:
        return self._request
