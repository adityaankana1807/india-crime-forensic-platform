from fastapi import APIRouter, Query

from app.services import clustering_service

router = APIRouter(prefix="/api/crime-analysis", tags=["crime-analysis"])


@router.get("/hotspots")
def hotspots(eps_km: float = Query(5.0, gt=0), min_samples: int = Query(10, gt=0)):
    return clustering_service.detect_hotspots(eps_km=eps_km, min_samples=min_samples)


@router.get("/trends")
def trends():
    return clustering_service.crime_trends()
