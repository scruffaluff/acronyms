"""Rest data schemas."""


from typing import Optional

from pydantic import BaseModel, Field


class AcronymBody(BaseModel):
    """Post request validator for Acronym type."""

    abbreviation: str = Field(
        title="Acronym abbreviation", max_length=30, min_length=1
    )
    description: Optional[str]
    phrase: str = Field(
        description="Acronym phrase", max_length=300, min_length=1
    )

    class Config:
        """Metadata for model."""

        schema_extra = {
            "example": {
                "abbreviation": "AM",
                "description": "Definition of amplitude modulation",
                "phrase": "Amplitude Modulation",
            }
        }
