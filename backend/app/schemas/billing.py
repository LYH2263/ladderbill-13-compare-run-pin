from pydantic import BaseModel, Field


class BillRequest(BaseModel):
    account_id: int | None = None
    kwh: float = Field(ge=0)
    peak: bool = False
    persist: bool = True


class CompareRequest(BaseModel):
    kwh: float = Field(ge=0)
    persist: bool = False


class CalcRunOut(BaseModel):
    id: int
    kind: str
    account_id: int | None
    input_json: str
    result_json: str
    created_at: str


class ComparePinRequest(BaseModel):
    kwh: float = Field(ge=0)


class CompareRunOut(BaseModel):
    id: int
    kwh: float
    plain_total: float
    peak_total: float
    delta: float
    peak_factor: float
    segments: dict | None = None
    created_at: str
    deleted_at: str | None = None


class CompareRunPage(BaseModel):
    items: list[CompareRunOut]
    page: int
    page_size: int
    total: int


class SettingsUpdateRequest(BaseModel):
    peak_factor: float = Field(gt=0)
