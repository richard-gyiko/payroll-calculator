from pathlib import Path
from typing import Annotated

from .api_contracts import (
    FlagsResponse,
    PayrollRequest,
    PayrollRequestModel,
    PayrollResponse,
)
from .engine import PayrollEngine
from fastapi import FastAPI, HTTPException, Query
from fastapi_mcp import FastApiMCP
from .loader import load_rules

app = FastAPI(
    title="Tax Calculator API",
    description="API for calculating taxes based on salary and personal conditions",
)


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

    try:
        compiled, _, _ = load_rules(json_path)
        engine = PayrollEngine(compiled)

        # Get required flags from the engine
        required_flags = engine.get_flags()

        # Start with the provided flags and add the date
        flags = request.flags.copy()
        flags["date"] = request.date.strftime("%Y-%m-%d")

        # Validate flags
        missing_flags = [
            flag for flag in required_flags if flag not in flags and flag != "date"
        ]
        if missing_flags:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required flags: {', '.join(missing_flags)}",
            )

        # Check for unsupported flags
        unsupported_flags = [
            flag for flag in flags if flag != "date" and flag not in required_flags
        ]
        if unsupported_flags:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported flags: {', '.join(unsupported_flags)}",
            )

        result = engine.run(request.gross, **flags)

        return PayrollResponse(
            date=request.date,
            gross=request.gross,
            net=result["net"],
            super_gross=result["super_gross"],
            breakdown=result["breakdown"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@app.get("/flags", operation_id="get_payroll_flags", response_model=FlagsResponse)
def get_flags(request: Annotated[PayrollRequestModel, Query()]) -> FlagsResponse:
    """Get available flags for the given calculation."""
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

        return FlagsResponse(flags=flags)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving flags: {str(e)}")


mcp = FastApiMCP(app, include_operations=["calculate_payroll"])

# Mount the MCP server directly to your FastAPI app
mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
