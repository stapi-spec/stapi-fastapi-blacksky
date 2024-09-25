from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from stapi_fastapi.models.constraints import Constraints as BaseConstraints
from stapi_fastapi.models.opportunity import OpportunityRequest


OFF_NADIR_RANGE = (0.0, 45.0)
OFF_NADIR_DEFAULT_RANGE = (0.0, 30.0)
OFF_NADIR_MIN_SPREAD = 5.0


class OffNadirRange(BaseModel):
    minimum: float = Field(ge=0.0, le=45)
    maximum: float = Field(ge=0.0, le=45)

    @model_validator(mode="after")
    def validate(self) -> "OffNadirRange":
        diff = self.maximum - self.minimum
        if diff < OFF_NADIR_MIN_SPREAD:
            raise ValueError(f"range must be at least {OFF_NADIR_MIN_SPREAD}°")
        return self


class CloudCoverRange(BaseModel):
    minimum: float = Field(ge=0.0, le=100)
    maximum: float = Field(ge=0.0, le=100)

    @model_validator(mode="after")
    def validate(self) -> "CloudCoverRange":
        diff = self.maximum - self.minimum
        if diff < 0:
            raise ValueError("Maximum must be more than minimum")
        return self


class Constraints(BaseConstraints):
    off_nadir: OffNadirRange = OffNadirRange(minimum=0.0, maximum=30.0)
    cloud_cover: CloudCoverRange = CloudCoverRange(minimum=0, maximum=100)


class ValidatedOpportunityRequest(OpportunityRequest):
    properties: Constraints
