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


class BreakdownItem(BaseModel):
    """Model for a single breakdown item in the payroll calculation."""

    label: str = Field(..., description="Human-readable label for the tax rule")
    amount: float = Field(..., description="Amount of the tax calculation")
    direction: str = Field(
        ...,
        description="Direction of the tax flow: 'employee', 'employer', or 'neutral'",
    )


class PayrollResponse(BaseModel):
    """Response model for payroll calculation."""

    date: datetime.date
    gross: int
    net: float
    super_gross: float
    breakdown: Dict[str, BreakdownItem] = Field(
        ...,
        description="Breakdown of tax calculations with rule ID as key and details including label, amount, and direction",
        example={
            "tb_jarulek": {
                "label": "TB-járulék 18,5 %",
                "amount": -18500.0,
                "direction": "employee",
            },
            "szja_full": {
                "label": "SZJA 15 %",
                "amount": -15000.0,
                "direction": "employee",
            },
        },
    )


class FlagsResponse(BaseModel):
    """Response model for available flags."""

    flags: List[str] = Field(
        ..., description="List of available flag names for the calculation"
    )
