from fastapi import APIRouter, HTTPException, Query

from app.schemas.billing import ComparePinRequest, SettingsUpdateRequest
from app.services.billing_service import BillingService

router = APIRouter(tags=["compare-runs"])


@router.post("/compare-runs", status_code=201)
def pin_compare_run(body: ComparePinRequest):
    with BillingService() as svc:
        return svc.pin_compare(body.kwh)


@router.get("/compare-runs")
def list_compare_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    with BillingService() as svc:
        return svc.list_compare_runs(page, page_size)


@router.get("/compare-runs/{run_id}")
def get_compare_run(run_id: int):
    with BillingService() as svc:
        row = svc.get_compare_run(run_id)
        if not row:
            raise HTTPException(404, "compare run not found")
        return row


@router.delete("/compare-runs/{run_id}")
def delete_compare_run(run_id: int):
    with BillingService() as svc:
        if not svc.delete_compare_run(run_id):
            raise HTTPException(404, "compare run not found")
        return {"ok": True, "id": run_id}
