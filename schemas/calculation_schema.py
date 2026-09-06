from typing import Literal

from pydantic import BaseModel


class Calculation(BaseModel):
    operation: Literal[
        "mean",
        "median",
        "min",
        "max",
        "range",
        "count",
        "difference",
        "percentage_change",
    ]
    column: str
    second_column: str | None = None
    first_value: str | None = None
    second_value: str | None = None


class CalculationPlan(BaseModel):
    calculations: list[Calculation]