from pydantic import BaseModel, Field


class BillRequest(BaseModel):
    account_id: int | None = None
    kwh: float = Field(ge=0)
    peak: bool = False
    persist: bool = True


class CompareRequest(BaseModel):
    kwh: float = Field(ge=0)
    persist: bool = False
    pinned: bool = False


class PeakFactorRequest(BaseModel):
    peak_factor: float = Field(gt=0)


class CalcRunOut(BaseModel):
    id: int
    kind: str
    account_id: int | None
    input_json: str
    result_json: str
    created_at: str
    pinned: bool = False
    pinned_at: str | None = None
    deleted_at: str | None = None
