from datetime import datetime, timedelta

from pydantic import AnyUrl, BaseModel, Field, field_validator

from littoral.models import MODEL_CONFIG

# local alias so we can mock datetime
_datetime = datetime


class OauthFlow(BaseModel):
    model_config = MODEL_CONFIG
    device_code: str
    user_code: str
    verification_url: AnyUrl = Field(alias="verificationUriComplete")
    interval: int
    expires_at: datetime = Field(alias="expiresIn")

    @field_validator("verification_url", mode="before")
    @classmethod
    def add_scheme(cls, v: str) -> str:
        return f"https://{v}" if not v.startswith("http") else v

    @field_validator("expires_at", mode="before")
    @classmethod
    def to_absolute(cls, v: float | datetime) -> datetime:
        if isinstance(v, _datetime):
            return v
        else:
            return datetime.now() + timedelta(seconds=v)
