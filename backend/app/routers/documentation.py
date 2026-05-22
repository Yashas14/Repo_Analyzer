"""
Documentation Router - Handles documentation generation and export
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.schemas import DocumentationRequest, DocumentationResponse
from app.services.documentation_service import DocumentationService
from app.services.analysis_service import AnalysisService
from datetime import datetime
import os

router = APIRouter()
doc_service = DocumentationService()
analysis_service = AnalysisService()


@router.post("/{repository_id}/generate", response_model=DocumentationResponse)
async def generate_documentation(repository_id: str, request: DocumentationRequest):
    """
    Generate documentation for a repository
    """
    try:
        # Check if repository exists and has been analyzed
        if not await analysis_service.repository_exists(repository_id):
            raise HTTPException(status_code=404, detail="Repository not found")
        
        analysis = await analysis_service.get_analysis_result(repository_id)
        
        # Generate documentation
        doc_path = await doc_service.generate_documentation(
            repository_id=repository_id,
            analysis=analysis,
            include_code_snippets=request.include_code_snippets,
            include_diagrams=request.include_diagrams,
            format=request.format
        )
        
        return DocumentationResponse(
            download_url=f"/api/documentation/{repository_id}/download?format={request.format}",
            format=request.format,
            generated_at=datetime.now()
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found or not analyzed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/download")
async def download_documentation(repository_id: str, format: str = "pdf"):
    """
    Download generated documentation
    """
    try:
        file_path = await doc_service.get_documentation_path(repository_id, format)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Documentation not found. Please generate it first.")
        
        # Determine media type
        media_types = {
            "pdf": "application/pdf",
            "markdown": "text/markdown",
            "html": "text/html"
        }
        
        extensions = {
            "pdf": ".pdf",
            "markdown": ".md",
            "html": ".html"
        }
        
        return FileResponse(
            path=file_path,
            media_type=media_types.get(format, "application/octet-stream"),
            filename=f"repository_documentation{extensions.get(format, '.pdf')}"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Documentation not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/preview")
async def preview_documentation(repository_id: str):
    """
    Get a preview of the documentation in HTML format
    """
    try:
        analysis = await analysis_service.get_analysis_result(repository_id)
        preview = await doc_service.generate_preview(analysis)
        return {"preview": preview}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found or not analyzed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/markdown")
async def get_markdown_documentation(repository_id: str):
    """
    Get documentation in Markdown format
    """
    try:
        analysis = await analysis_service.get_analysis_result(repository_id)
        markdown = await doc_service.generate_markdown(analysis)
        return {"markdown": markdown}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found or not analyzed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
