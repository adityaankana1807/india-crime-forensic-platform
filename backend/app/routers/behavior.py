from fastapi import APIRouter, HTTPException

from app.services import behavior_service

router = APIRouter(prefix="/api/behavior", tags=["behavior"])


@router.get("/profiles")
def list_profiles():
    return behavior_service.list_profiles()


@router.get("/profiles/{suspect_id}")
def profile_detail(suspect_id: str):
    detail = behavior_service.get_profile_detail(suspect_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"suspect '{suspect_id}' not found")
    return detail


@router.post("/profiles/{suspect_id}/narrative")
def profile_narrative(suspect_id: str):
    result = behavior_service.generate_narrative(suspect_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"suspect '{suspect_id}' not found")
    return result
