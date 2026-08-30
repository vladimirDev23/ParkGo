import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

PLATE_PATTERN = re.compile(r"^[\w\- ]{2,20}$", re.UNICODE)


class VehicleBase(BaseModel):
    plate_number: str = Field(min_length=2, max_length=20)
    region_code: str = Field(default="", max_length=10)
    display_name: str = Field(min_length=1, max_length=100)
    brand: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=80)
    color: str | None = Field(default=None, max_length=50)

    @field_validator("plate_number")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        normalized = " ".join(value.upper().strip().split())
        if not PLATE_PATTERN.fullmatch(normalized):
            raise ValueError("Plate contains unsupported characters")
        return normalized

    @field_validator("region_code")
    @classmethod
    def normalize_region(cls, value: str) -> str:
        return value.upper().strip()


class VehicleCreate(VehicleBase):
    is_default: bool = False


class VehicleUpdate(BaseModel):
    plate_number: str | None = Field(default=None, min_length=2, max_length=20)
    region_code: str | None = Field(default=None, max_length=10)
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    brand: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=80)
    color: str | None = Field(default=None, max_length=50)

    @field_validator("plate_number")
    @classmethod
    def normalize_plate(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return VehicleBase.normalize_plate(value)


class VehicleResponse(VehicleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_default: bool
    created_at: datetime
