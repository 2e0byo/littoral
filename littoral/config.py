from typing import Self

from pydantic import AnyHttpUrl, BaseModel


class Urls(BaseModel):
    api_v1: AnyHttpUrl
    api_v2: AnyHttpUrl
    oauth2: AnyHttpUrl
    image: AnyHttpUrl
    video: AnyHttpUrl

    @classmethod
    def default(cls) -> Self:
        return cls(
            api_v1="https://api.tidal.com/v1",  # type: ignore
            api_v2="https://api.tidal.com/v2",  # type: ignore
            oauth2="https://auth.tidal.com/v1/oauth2/token",  # type: ignore
            image="https://resources.tidal.com/images",  # type: ignore
            video="https://resources.tidal.com/videos",  # type: ignore
        )


URLS = Urls.default()
