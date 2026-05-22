"""
Analysis Router - Handles repository analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from app.models.schemas import AnalysisResult, ProjectExplanation
from app.services.analysis_service import AnalysisService
from app.services.ai_service import AIService
from typing import Optional, List
import os

router = APIRouter()
analysis_service = AnalysisService()
ai_service = AIService()


@router.post("/{repository_id}/analyze")
async def analyze_repository(repository_id: str, background_tasks: BackgroundTasks):
    """
    Start analysis of a repository
    """
    try:
        # Check if repository exists
        if not await analysis_service.repository_exists(repository_id):
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Start analysis
        result = await analysis_service.analyze_repository(repository_id)
        
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/status")
async def get_analysis_status(repository_id: str):
    """
    Get the status of repository analysis
    """
    try:
        status = await analysis_service.get_analysis_status(repository_id)
        return status
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/result")
async def get_analysis_result(repository_id: str):
    """
    Get the analysis result for a repository
    """
    try:
        result = await analysis_service.get_analysis_result(repository_id)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/functionalities")
async def get_functionalities(repository_id: str):
    """
    Get all identified functionalities in the repository
    """
    try:
        functionalities = await analysis_service.get_functionalities(repository_id)
        return {"functionalities": functionalities}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/modules")
async def get_modules(repository_id: str):
    """
    Get all identified modules in the repository
    """
    try:
        modules = await analysis_service.get_modules(repository_id)
        return {"modules": modules}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repository_id}/explain")
async def explain_project(repository_id: str):
    """
    Get AI-powered explanation of the project
    """
    try:
        # Get analysis result first
        analysis = await analysis_service.get_analysis_result(repository_id)
        
        # Generate AI explanation
        explanation = await ai_service.explain_project(analysis)
        
        return explanation
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/architecture")
async def get_architecture(repository_id: str):
    """
    Get the architecture overview of the repository
    """
    try:
        architecture = await analysis_service.get_architecture(repository_id)
        return {"architecture": architecture}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/tech-stack")
async def get_tech_stack(repository_id: str):
    """
    Get the technology stack used in the repository
    """
    try:
        tech_stack = await analysis_service.get_tech_stack(repository_id)
        return {"tech_stack": tech_stack}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/dependencies")
async def get_dependencies(repository_id: str):
    """
    Get all dependencies identified in the repository
    """
    try:
        dependencies = await analysis_service.get_dependencies(repository_id)
        return {"dependencies": dependencies}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repository_id}/explain-functionality")
async def explain_functionality_detailed(
    repository_id: str,
    functionality_name: str = Query(..., description="Name of the functionality to explain"),
    max_files: int = Query(5, description="Maximum number of files to analyze")
):
    """
    Get a detailed line-by-line explanation of a specific functionality.
    This provides in-depth code analysis explaining every line and why it's used.
    """
    try:
        # Get analysis result
        analysis = await analysis_service.get_analysis_result(repository_id)
        
        # Find the functionality
        functionality = None
        for func in analysis.get('functionalities', []):
            if func.get('name', '').lower() == functionality_name.lower():
                functionality = func
                break
        
        if not functionality:
            raise HTTPException(
                status_code=404, 
                detail=f"Functionality '{functionality_name}' not found"
            )
        
        # Get the repository path
        repo_path = await analysis_service.get_repository_path(repository_id)
        
        # Read the related files
        code_files = {}
        files_to_read = functionality.get('files', [])[:max_files]
        
        for file_path in files_to_read:
            full_path = os.path.join(repo_path, file_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Limit file size to avoid token limits
                        if len(content) > 10000:
                            content = content[:10000] + "\n\n... (truncated for analysis)"
                        code_files[file_path] = content
                except Exception as e:
                    code_files[file_path] = f"Error reading file: {str(e)}"
        
        # If no files found, try to find them based on functionality name
        if not code_files:
            # Search for files that might be related
            search_terms = functionality_name.lower().replace('_', ' ').replace('-', ' ').split()
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden and common non-code directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'dist', 'build']]
                
                for file in files:
                    if len(code_files) >= max_files:
                        break
                    
                    file_lower = file.lower()
                    if any(term in file_lower for term in search_terms):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, repo_path)
                        try:
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if len(content) > 10000:
                                    content = content[:10000] + "\n\n... (truncated for analysis)"
                                code_files[rel_path] = content
                        except:
                            pass
        
        if not code_files:
            return {
                "functionality": functionality,
                "explanation": {
                    "overview": functionality.get('description', 'No description'),
                    "purpose": functionality.get('core_logic', 'No core logic'),
                    "how_it_works": "No code files found for this functionality",
                    "file_explanations": [],
                    "data_flow": "Unable to analyze without code files",
                    "dependencies": [],
                    "patterns_used": [],
                    "best_practices": [],
                    "potential_improvements": []
                },
                "files_analyzed": []
            }
        
        # Generate detailed explanation
        explanation = await ai_service.explain_functionality_detailed(
            functionality, 
            code_files, 
            analysis
        )
        
        return {
            "functionality": functionality,
            "explanation": explanation,
            "files_analyzed": list(code_files.keys())
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repository_id}/explain-code")
async def explain_code_block(
    repository_id: str,
    file_path: str = Query(..., description="Path to the file"),
    start_line: int = Query(1, description="Start line number"),
    end_line: int = Query(None, description="End line number (optional)")
):
    """
    Get a detailed line-by-line explanation of a specific code block.
    """
    try:
        # Get the repository path
        repo_path = await analysis_service.get_repository_path(repository_id)
        full_path = os.path.join(repo_path, file_path)
        
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Read the file
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Extract the requested lines
        if end_line is None:
            end_line = len(lines)
        
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        code = ''.join(lines[start_idx:end_idx])
        
        # Detect language from file extension
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript/React',
            '.tsx': 'TypeScript/React',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.sql': 'SQL',
            '.sh': 'Bash',
            '.ps1': 'PowerShell',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.less': 'LESS',
        }
        language = language_map.get(ext, 'Unknown')
        
        # Get analysis for context
        try:
            analysis = await analysis_service.get_analysis_result(repository_id)
            context = f"This code is part of {analysis.get('repository_name', 'the project')}. Tech stack: {', '.join(analysis.get('tech_stack', []))}"
        except:
            context = ""
        
        # Generate explanation
        explanation = await ai_service.explain_code_block(code, language, context)
        
        return {
            "file_path": file_path,
            "start_line": start_line,
            "end_line": end_line,
            "language": language,
            "code": code,
            "explanation": explanation
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository or file not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
