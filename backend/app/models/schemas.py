"""
Pydantic Models/Schemas for the API
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class RepositorySource(str, Enum):
    ZIP_UPLOAD = "zip_upload"
    GIT_CLONE = "git_clone"


class RepositoryInput(BaseModel):
    """Input model for repository URL"""
    url: str = Field(..., description="Git repository URL (HTTPS or SSH)")
    branch: Optional[str] = Field(default="main", description="Branch to clone")


class FileInfo(BaseModel):
    """Information about a single file"""
    path: str
    name: str
    extension: str
    size: int
    lines: int
    language: Optional[str] = None
    purpose: Optional[str] = None


class ModuleInfo(BaseModel):
    """Information about a module/component"""
    name: str
    path: str
    description: Optional[str] = None
    files: List[FileInfo] = []
    dependencies: List[str] = []
    responsibilities: List[str] = []


class FunctionalityInfo(BaseModel):
    """Information about a functionality"""
    name: str
    description: str
    files: List[str] = []
    modules: List[str] = []
    core_logic: Optional[str] = None


class DependencyInfo(BaseModel):
    """Dependency information"""
    name: str
    version: Optional[str] = None
    type: str  # "runtime", "dev", "peer"


class RepositoryStructure(BaseModel):
    """Complete repository structure"""
    name: str
    path: str
    total_files: int
    total_lines: int
    languages: Dict[str, int] = {}  # language -> file count
    modules: List[ModuleInfo] = []
    files: List[FileInfo] = []
    dependencies: List[DependencyInfo] = []


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    repository_id: str
    repository_name: str
    analysis_date: datetime
    structure: RepositoryStructure
    functionalities: List[FunctionalityInfo] = []
    architecture: Optional[str] = None
    tech_stack: List[str] = []
    summary: Optional[str] = None


class ProjectExplanation(BaseModel):
    """AI-generated project explanation"""
    what: str = Field(..., description="What the project does")
    why: str = Field(..., description="Why the project was developed")
    how: str = Field(..., description="How the project works")
    architecture: str = Field(..., description="High-level architecture")
    workflow: str = Field(..., description="Main workflow")
    functionalities: List[Dict[str, str]] = Field(..., description="Functionality explanations")


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Chat request model"""
    repository_id: str
    message: str
    conversation_history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    related_files: List[str] = []
    code_snippets: List[Dict[str, str]] = []


class DocumentationRequest(BaseModel):
    """Documentation generation request"""
    repository_id: str
    include_code_snippets: bool = True
    include_diagrams: bool = True
    format: str = "pdf"  # "pdf", "markdown", "html"


class DocumentationResponse(BaseModel):
    """Documentation generation response"""
    download_url: str
    format: str
    generated_at: datetime


class UploadResponse(BaseModel):
    """Response after uploading a repository"""
    repository_id: str
    name: str
    source: RepositorySource
    file_count: int
    message: str
