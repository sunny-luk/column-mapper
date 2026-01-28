import os
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Depends, Form
from app.core.csv_service import CSVService
from app.core.mapping_engine import MappingEngine
from app.core.repository import SQLiteRepository
from app.core.schemas.user_info import UserInfo
from app.core.mapping_strategies.case_insensitive import CaseInsensitiveMappingStrategy
from typing import Annotated
from pydantic import BaseModel

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
STORAGE_PATH = os.getenv("STORAGE_PATH", "data/csv_storage")
DB_PATH = os.getenv("DB_PATH", "sqlite.db")


# Dependency Providers
def get_csv_service():
    return CSVService(STORAGE_PATH)


def get_repository():
    return SQLiteRepository(DB_PATH)


def get_mapping_engine():
    return MappingEngine(UserInfo)


def get_schema():
    return UserInfo


CSVServiceDep = Annotated[CSVService, Depends(get_csv_service)]
RepoDep = Annotated[SQLiteRepository, Depends(get_repository)]
EngineDep = Annotated[MappingEngine, Depends(get_mapping_engine)]

app = FastAPI(title="Column Mapper API")


@app.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_file(
    file: UploadFile = File(...),
    has_header: bool = Form(True),
    apply_mapping_name: str = Form(None),
    csv_service: CSVServiceDep = None,
    repository: RepoDep = None,
    mapping_engine: EngineDep = None,
    schema: type[BaseModel] = Depends(get_schema),
):
    # File size validation
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File size exceeds 100MB limit.",
        )

    # Save file to storage
    try:
        saved_path = csv_service.save_upload(file.filename, file.file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Map columns
    source_columns = csv_service.get_columns(saved_path, has_header=has_header)

    if not source_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not parse columns. Please check if the file is a valid CSV.",
        )

    if apply_mapping_name:
        saved_mapping = repository.get_mapping(apply_mapping_name)
        if not saved_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not find saved mapping {apply_mapping_name}.",
            )
    else:
        saved_mapping = None

    suggested_mapping = mapping_engine.run(
        source_columns=source_columns,
        saved_mapping=saved_mapping,
        mapping_strategy=CaseInsensitiveMappingStrategy(),
    )

    return {
        "filename": file.filename,
        "saved_filename": os.path.basename(saved_path),
        "source_columns": source_columns,
        "target_fields": list(schema.model_fields.keys()),
        "suggested_mapping": suggested_mapping,
    }
