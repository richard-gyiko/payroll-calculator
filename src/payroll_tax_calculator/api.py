import datetime
from pathlib import Path
from typing import Annotated, Any, Dict

from engine import PayrollEngine
from fastapi import FastAPI, HTTPException, Query
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

    # Start with the provided flags and add the date
    flags = request.flags.copy()
    flags["date"] = request.date.strftime("%Y-%m-%d")

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


class PayrollFlagsRequest(BaseModel):
    """Request model for payroll flags."""

    country: str = Field(..., description="Country code (e.g., 'hu' for Hungary)")
    date: datetime.date = Field(
        ..., description="Date of the payroll calculation (YYYY-MM-DD)"
    )


@app.get("/flags", operation_id="get_payroll_flags")
def get_flags(request: Annotated[PayrollFlagsRequest, Query()]) -> Dict[str, Any]:
    """Get available flags for the given year."""
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

    try:
        compiled, _, _ = load_rules(json_path)
        engine = PayrollEngine(compiled)
        flags = engine.get_flags()

        # Exclude 'date' from the flags as it's provided in the request
        flags = [flag for flag in flags if flag != "date"]

        return {"flags": flags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving flags: {str(e)}")


mcp = FastApiMCP(app, include_operations=["calculate_payroll"])

# Mount the MCP server directly to your FastAPI app
mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
