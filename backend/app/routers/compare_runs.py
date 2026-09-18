from fastapi import APIRouter, HTTPException

from app.services.billing_service import BillingService

router = APIRouter(tags=["compare-runs"])


@router.get("/compare/runs")
def list_compare_runs(page: int = 1, page_size: int = 20):
    """分页列表；软删除记录默认不可见，钉选记录排在最前。"""
    with BillingService() as svc:
        return svc.list_compare_runs(page, page_size)


@router.get("/compare/runs/{run_id}")
def get_compare_run(run_id: int):
    """详情查询：即使已被软删除，按 id 仍可读到完整快照。"""
    with BillingService() as svc:
        row = svc.get_run(run_id)
        if not row or row["kind"] != "compare":
            raise HTTPException(404, "compare run not found")
        return row


@router.post("/compare/runs/{run_id}/pin")
def pin_compare_run(run_id: int):
    with BillingService() as svc:
        row = svc.pin_compare_run(run_id, True)
        if not row:
            raise HTTPException(404, "compare run not found")
        return row


@router.delete("/compare/runs/{run_id}/pin")
def unpin_compare_run(run_id: int):
    with BillingService() as svc:
        row = svc.pin_compare_run(run_id, False)
        if not row:
            raise HTTPException(404, "compare run not found")
        return row


@router.delete("/compare/runs/{run_id}")
def delete_compare_run(run_id: int):
    """软删除：列表不可见，但详情仍可读。"""
    with BillingService() as svc:
        row = svc.delete_compare_run(run_id)
        if not row:
            raise HTTPException(404, "compare run not found")
        return row
