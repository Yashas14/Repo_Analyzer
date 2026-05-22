"""
Repository Router - Handles repository upload and cloning
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.models.schemas import RepositoryInput, UploadResponse, RepositorySource
from app.services.repository_service import RepositoryService
from app.config import settings
import uuid
import os

router = APIRouter()
repo_service = RepositoryService()


@router.post("/upload", response_model=UploadResponse)
async def upload_repository(file: UploadFile = File(...)):
    """
    Upload a repository as a ZIP file
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    try:
        # Generate unique repository ID
        repo_id = str(uuid.uuid4())
        
        # Save and extract the repository
        result = await repo_service.process_uploaded_zip(file, repo_id)
        
        return UploadResponse(
            repository_id=repo_id,
            name=result["name"],
            source=RepositorySource.ZIP_UPLOAD,
            file_count=result["file_count"],
            message="Repository uploaded and extracted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clone", response_model=UploadResponse)
async def clone_repository(repo_input: RepositoryInput):
    """
    Clone a repository from a Git URL
    """
    try:
        # Generate unique repository ID
        repo_id = str(uuid.uuid4())
        
        # Clone the repository
        result = await repo_service.clone_repository(
            repo_input.url, 
            repo_id, 
            repo_input.branch
        )
        
        return UploadResponse(
            repository_id=repo_id,
            name=result["name"],
            source=RepositorySource.GIT_CLONE,
            file_count=result["file_count"],
            message="Repository cloned successfully"
        )
    except Exception as e:
        import traceback
        error_detail = str(e) if str(e) else traceback.format_exc()
        print(f"Clone error: {error_detail}")  # Log to console
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/{repository_id}/structure")
async def get_repository_structure(repository_id: str):
    """
    Get the file structure of a repository
    """
    try:
        structure = await repo_service.get_repository_structure(repository_id)
        return structure
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/file")
async def get_file_content(repository_id: str, file_path: str):
    """
    Get the content of a specific file
    """
    try:
        content = await repo_service.get_file_content(repository_id, file_path)
        return {"path": file_path, "content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{repository_id}")
async def delete_repository(repository_id: str):
    """
    Delete a repository and its data
    """
    try:
        await repo_service.delete_repository(repository_id)
        return {"message": "Repository deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_repositories():
    """
    List all uploaded/cloned repositories
    """
    try:
        repos = await repo_service.list_repositories()
        return {"repositories": repos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
