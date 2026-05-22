"""
Chat Router - Handles interactive Q&A
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, ChatMessage
from app.services.chat_service import ChatService
from app.services.analysis_service import AnalysisService
from typing import List

router = APIRouter()
chat_service = ChatService()
analysis_service = AnalysisService()


@router.post("/{repository_id}/ask", response_model=ChatResponse)
async def ask_question(repository_id: str, request: ChatRequest):
    """
    Ask a natural language question about the repository
    """
    try:
        # Check if repository exists and has been analyzed
        if not await analysis_service.repository_exists(repository_id):
            raise HTTPException(status_code=404, detail="Repository not found")
        
        analysis = await analysis_service.get_analysis_result(repository_id)
        
        # Get response from chat service
        response = await chat_service.answer_question(
            repository_id=repository_id,
            question=request.message,
            analysis=analysis,
            conversation_history=request.conversation_history
        )
        
        return response
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found or not analyzed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/suggestions")
async def get_question_suggestions(repository_id: str):
    """
    Get suggested questions for the repository
    """
    try:
        if not await analysis_service.repository_exists(repository_id):
            raise HTTPException(status_code=404, detail="Repository not found")
        
        analysis = await analysis_service.get_analysis_result(repository_id)
        suggestions = await chat_service.generate_question_suggestions(analysis)
        
        return {"suggestions": suggestions}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repository_id}/explain-file")
async def explain_file(repository_id: str, file_path: str):
    """
    Get AI explanation of a specific file
    """
    try:
        explanation = await chat_service.explain_file(repository_id, file_path)
        return {"file_path": file_path, "explanation": explanation}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repository_id}/explain-module")
async def explain_module(repository_id: str, module_name: str):
    """
    Get AI explanation of a specific module
    """
    try:
        analysis = await analysis_service.get_analysis_result(repository_id)
        explanation = await chat_service.explain_module(analysis, module_name)
        return {"module_name": module_name, "explanation": explanation}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Module not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repository_id}/find-files")
async def find_related_files(repository_id: str, query: str):
    """
    Find files related to a specific query/functionality
    """
    try:
        analysis = await analysis_service.get_analysis_result(repository_id)
        files = await chat_service.find_related_files(analysis, query)
        return {"query": query, "related_files": files}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
