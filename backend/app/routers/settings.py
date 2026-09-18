from fastapi import APIRouter, HTTPException

from app.schemas.billing import SettingsUpdateRequest
from app.services.billing_service import BillingService

router = APIRouter(tags=["settings"])


@router.get("/settings")
def get_settings():
    with BillingService() as svc:
        return svc.settings_map()


@router.put("/settings")
def update_settings(body: SettingsUpdateRequest):
    with BillingService() as svc:
        try:
            return svc.update_settings(body.model_dump())
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
