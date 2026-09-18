from fastapi import APIRouter

from app.schemas.billing import PeakFactorRequest
from app.services.billing_service import BillingService

router = APIRouter(tags=["settings"])


@router.get("/settings")
def get_settings():
    with BillingService() as svc:
        return svc.settings_map()


@router.put("/settings/peak_factor")
def update_peak_factor(body: PeakFactorRequest):
    """修改全局尖峰系数；仅影响之后的新对比，已钉选快照不变。"""
    with BillingService() as svc:
        factor = svc.update_peak_factor(body.peak_factor)
        return {"peak_factor": factor}
