import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class PayrollRequestModel(BaseModel):
    country: str = Field(
        ...,
        description="The taxing county. Two-letter country code (ISO 3166-1 alpha-2)",
    )
    date: datetime.date = Field(
        ..., description="Date of the payroll calculation (YYYY-MM-DD)"
    )


class PayrollRequest(PayrollRequestModel):
    """Request model for payroll calculation."""

    gross: int = Field(..., description="Gross salary")
    flags: Dict[str, Any] = Field(
        default_factory=dict, description="Dynamic flags for calculation"
    )


class PayrollResponse(BaseModel):
    """Response model for payroll calculation."""

    date: datetime.date
    gross: int
    net: float
    super_gross: float
    flags: Dict[str, Any]
    breakdown: Dict[str, Dict[str, Any]]


class FlagsResponse(BaseModel):
    """Response model for available flags."""

    flags: List[str] = Field(
        ..., description="List of available flag names for the calculation"
    )
