import os
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Depends, Form
from fastapi.staticfiles import StaticFiles
from app.core.csv_service import CSVService
from app.core.mapping_engine import MappingEngine
from app.core.repository import SQLiteRepository
from app.core.schemas.user_info import UserInfo
from app.core.mapping_strategies.case_insensitive import CaseInsensitiveMappingStrategy
from app.core.mapping_strategies.fuzzy_match import FuzzyMatchMappingStrategy
from app.core.validators.exceptions import ValidationException
from app.core.validators.required_columns import RequiredColumnsValidator
from app.core.validators.missing_value_columns import MissingValueColumnsValidator
from typing import Annotated, Dict
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

# Get the directory where main.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to your static folder
static_path = os.path.join(current_dir, "ui")

app.mount("/ui", StaticFiles(directory=static_path), name="ui")


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
        mapping_strategy=FuzzyMatchMappingStrategy(),
    )

    return {
        "filename": file.filename,
        "saved_filename": os.path.basename(saved_path),
        "source_columns": source_columns,
        "target_fields": list(schema.model_fields.keys()),
        "suggested_mapping": suggested_mapping,
    }


@app.get("/mappings")
def list_mappings(repository: RepoDep):
    """Returns all saved mappings for the UI dropdown."""
    try:
        mappings = repository.list_mappings()
        return {"mappings": mappings}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


class ValidationRequest(BaseModel):
    filename: str
    mapping: Dict[str, str | None]


@app.post("/validate")
def validate_mapping(
    request: ValidationRequest,
    schema: type[BaseModel] = Depends(get_schema),
    csv_service: CSVService = Depends(get_csv_service),
):
    validators = [
        RequiredColumnsValidator(),
        MissingValueColumnsValidator(
            filename=request.filename, csv_service=csv_service
        ),
    ]
    errors = {}

    for validator in validators:
        try:
            validator.validate(request.mapping, schema)
        except ValidationException as e:
            errors[validator.validation_category()] = str(e)

    if errors:
        raise HTTPException(
            status_code=400,
            detail="\n".join(
                [f"{cat}: {error_msg}" for cat, error_msg in errors.items()]
            ),
        )

    return {
        "status": "success",
        "message": "All required columns mapped successfully.",
        "mapped_count": len(request.mapping),
    }


class SaveMappingRequest(BaseModel):
    mapping_name: str
    mapping: Dict[str, str | None]


@app.post("/process")
def process_and_save(request: SaveMappingRequest, repository: RepoDep = None):
    # Unique name check
    if repository.get_mapping(request.mapping_name):
        raise HTTPException(
            status_code=400,
            detail=f"Mapping name '{request.mapping_name}' already exists. Please choose another.",
        )

    # Save the mapping
    repository.save_mapping(request.mapping_name, request.mapping)

    return {"mapping_name": request.mapping_name}
