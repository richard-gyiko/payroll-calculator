import datetime
from pathlib import Path
from typing import Any, Dict

from engine import PayrollEngine
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from loader import load_rules
from pydantic import BaseModel, Field

app = FastAPI(
    title="Tax Calculator API",
    description="API for calculating taxes based on salary and personal conditions",
)


class PayrollRequest(BaseModel):
    """Request model for payroll calculation."""

    country: str = Field(..., description="Country code (e.g., 'hu' for Hungary)")
    date: datetime.date = Field(
        ..., description="Date of the payroll calculation (YYYY-MM-DD)"
    )
    gross: int = Field(..., description="Gross salary")
    mother_under30: bool = Field(False, description="Mother under 30 years old")
    under25: bool = Field(False, description="Person under 25 years old")
    children: int = Field(0, description="Number of children")
    entrant: bool = Field(False, description="First-time job entrant")
    months_on_job: int = Field(0, description="Months on current job")


class PayrollResponse(BaseModel):
    """Response model for payroll calculation."""

    date: datetime.date
    gross: int
    net: float
    super_gross: float
    flags: Dict[str, Any]
    breakdown: Dict[str, Dict[str, Any]]


@app.post(
    "/calculate", operation_id="calculate_payroll", response_model=PayrollResponse
)
async def calculate_payroll(request: PayrollRequest) -> PayrollResponse:
    """Calculate wage with tax deductions for the given year."""
    if request.date.year not in (2024, 2025):
        raise HTTPException(
            status_code=400,
            detail=f"Year must be either 2024 or 2025, got {request.date.year}",
        )

    json_path = Path(f"dsl/{request.country}{request.date.year}/dsl.jsonc")
    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Configuration file for year {request.date.year} and country {request.country} not found",
        )

    flags = {
        "mother_under30": request.mother_under30,
        "under25": request.under25,
        "children": request.children,
        "entrant": request.entrant,
        "months_on_job": request.months_on_job,
        "date": request.date.strftime("%Y-%m-%d"),
    }

    try:
        compiled, _, _ = load_rules(json_path)
        engine = PayrollEngine(compiled)
        result = engine.run(request.gross, **flags)

        return PayrollResponse(
            date=request.date,
            gross=request.gross,
            net=result["net"],
            super_gross=result["super_gross"],
            flags=flags,
            breakdown=result["breakdown"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


mcp = FastApiMCP(app, include_operations=["calculate_payroll"])

# Mount the MCP server directly to your FastAPI app
mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
