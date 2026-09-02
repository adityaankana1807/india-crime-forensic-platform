from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services import dataset_service

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("")
def list_datasets():
    return dataset_service.list_datasets()


@router.get("/{name}/stats")
def dataset_stats(name: str, preview_rows: int = 10):
    try:
        return dataset_service.get_stats(name, preview_rows)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"dataset '{name}' not found")


@router.get("/{name}/download")
def download_dataset(name: str):
    try:
        path = dataset_service.get_path(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"dataset '{name}' not found")
    return FileResponse(path, filename=name, media_type="text/csv")


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="only .csv files are supported")
    content = await file.read()
    return dataset_service.save_upload(file.filename, content)
