"""
Chat Service - Handles interactive Q&A functionality
"""

import os
from typing import Dict, List, Any
from app.services.ai_service import AIService
from app.services.repository_service import RepositoryService
from app.models.schemas import ChatResponse, ChatMessage


class ChatService:
    """Service for interactive Q&A about repositories"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.repo_service = RepositoryService()
    
    async def answer_question(
        self, 
        repository_id: str, 
        question: str, 
        analysis: Dict,
        conversation_history: List[ChatMessage] = None
    ) -> ChatResponse:
        """Answer a question about the repository"""
        
        # Get relevant code context based on the question
        code_context = await self._get_relevant_context(repository_id, question, analysis)
        
        # Get AI response
        answer = await self.ai_service.answer_question(
            question=question,
            analysis=analysis,
            code_context=code_context,
            conversation_history=conversation_history
        )
        
        # Find related files
        related_files = await self._find_related_files_for_question(question, analysis)
        
        # Extract any code snippets mentioned
        code_snippets = self._extract_code_snippets(answer)
        
        return ChatResponse(
            message=answer,
            related_files=related_files,
            code_snippets=code_snippets
        )
    
    async def generate_question_suggestions(self, analysis: Dict) -> List[str]:
        """Generate suggested questions based on the analysis"""
        suggestions = [
            f"What does this project do?",
            f"Explain the architecture of {analysis.get('repository_name', 'this project')}",
            "What problem does this code solve?",
            "How is the codebase organized?",
        ]
        
        # Add module-specific questions
        modules = analysis.get("modules", [])
        if modules:
            suggestions.append(f"What is the purpose of the {modules[0]['name']} module?")
            if len(modules) > 1:
                suggestions.append(f"How does {modules[0]['name']} interact with {modules[1]['name']}?")
        
        # Add functionality-specific questions
        functionalities = analysis.get("functionalities", [])
        if functionalities:
            suggestions.append(f"Explain how {functionalities[0]['name']} works")
        
        # Add tech-stack questions
        tech_stack = analysis.get("tech_stack", [])
        if tech_stack:
            suggestions.append(f"Why was {tech_stack[0]} chosen for this project?")
        
        # Add common questions
        suggestions.extend([
            "Which files handle the main business logic?",
            "What are the key dependencies?",
            "How can I contribute to this project?",
            "What are the entry points of the application?"
        ])
        
        return suggestions[:10]  # Return top 10 suggestions
    
    async def explain_file(self, repository_id: str, file_path: str) -> str:
        """Explain a specific file"""
        try:
            content = await self.repo_service.get_file_content(repository_id, file_path)
            
            if not self.ai_service.client:
                return self._get_basic_file_explanation(file_path, content)
            
            system_prompt = """You are a code expert. Explain the provided file including:
1. Purpose of the file
2. Key functions/classes and what they do
3. How it fits into the larger codebase
4. Any notable patterns or practices used

Be concise but thorough."""
            
            user_prompt = f"""Explain this file:

FILE: {file_path}

CONTENT:
{content[:10000]}"""
            
            return await self.ai_service._call_ai(system_prompt, user_prompt)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
    
    def _get_basic_file_explanation(self, file_path: str, content: str) -> str:
        """Get basic file explanation without AI"""
        lines = content.split('\n')
        
        explanation = f"## File: {file_path}\n\n"
        explanation += f"- **Lines of code:** {len(lines)}\n"
        explanation += f"- **Size:** {len(content)} characters\n\n"
        
        # Try to detect file type and purpose
        _, ext = os.path.splitext(file_path)
        
        file_types = {
            ".py": "Python source file",
            ".js": "JavaScript source file",
            ".ts": "TypeScript source file",
            ".jsx": "React JSX component",
            ".tsx": "React TSX component",
            ".java": "Java source file",
            ".html": "HTML template",
            ".css": "CSS stylesheet",
            ".json": "JSON configuration/data file",
            ".yaml": "YAML configuration file",
            ".yml": "YAML configuration file",
            ".md": "Markdown documentation",
            ".sql": "SQL database script"
        }
        
        explanation += f"**Type:** {file_types.get(ext, 'Source file')}\n\n"
        
        # Show first few lines as preview
        preview_lines = lines[:20]
        explanation += "**Preview:**\n```\n"
        explanation += '\n'.join(preview_lines)
        if len(lines) > 20:
            explanation += f"\n... ({len(lines) - 20} more lines)"
        explanation += "\n```\n\n"
        
        explanation += "*Detailed explanation requires AI configuration.*"
        
        return explanation
    
    async def explain_module(self, analysis: Dict, module_name: str) -> str:
        """Explain a specific module"""
        modules = analysis.get("modules", [])
        target_module = None
        
        for module in modules:
            if module["name"].lower() == module_name.lower():
                target_module = module
                break
        
        if not target_module:
            raise FileNotFoundError(f"Module not found: {module_name}")
        
        if not self.ai_service.client:
            return self._get_basic_module_explanation(target_module, analysis)
        
        system_prompt = """You are a software architect. Explain the module including:
1. Purpose and responsibility
2. Key components/files
3. How it interacts with other modules
4. Design patterns used

Be clear and educational."""
        
        functionalities = analysis.get("functionalities", [])
        related_funcs = [f for f in functionalities if module_name.lower() in f.get("name", "").lower()]
        
        user_prompt = f"""Explain this module:

MODULE: {target_module['name']}
PATH: {target_module.get('path', 'N/A')}
FILES: {', '.join(target_module.get('files', [])[:10])}
FILE COUNT: {target_module.get('file_count', 0)}

RELATED FUNCTIONALITIES: {related_funcs}

PROJECT TECH STACK: {', '.join(analysis.get('tech_stack', []))}"""
        
        return await self.ai_service._call_ai(system_prompt, user_prompt)
    
    def _get_basic_module_explanation(self, module: Dict, analysis: Dict) -> str:
        """Get basic module explanation without AI"""
        explanation = f"## Module: {module['name']}\n\n"
        explanation += f"**Path:** {module.get('path', 'N/A')}\n"
        explanation += f"**File Count:** {module.get('file_count', 0)}\n\n"
        
        files = module.get("files", [])
        if files:
            explanation += "**Files:**\n"
            for f in files[:15]:
                explanation += f"- {f}\n"
            if len(files) > 15:
                explanation += f"- ... and {len(files) - 15} more files\n"
        
        explanation += "\n*Detailed module explanation requires AI configuration.*"
        
        return explanation
    
    async def find_related_files(self, analysis: Dict, query: str) -> List[Dict[str, str]]:
        """Find files related to a query"""
        related_files = []
        query_lower = query.lower()
        
        # Search in functionalities
        for func in analysis.get("functionalities", []):
            if query_lower in func.get("name", "").lower() or query_lower in func.get("description", "").lower():
                for file_path in func.get("files", []):
                    related_files.append({
                        "path": file_path,
                        "reason": f"Part of {func['name']} functionality"
                    })
        
        # Search in file names
        structure = analysis.get("structure", {})
        for file_info in structure.get("files", []):
            file_path = file_info.get("path", "")
            file_name = file_info.get("name", "")
            
            if query_lower in file_name.lower() or query_lower in file_path.lower():
                if not any(f["path"] == file_path for f in related_files):
                    related_files.append({
                        "path": file_path,
                        "reason": "File name matches query"
                    })
        
        # Search in modules
        for module in analysis.get("modules", []):
            if query_lower in module.get("name", "").lower():
                for file_path in module.get("files", [])[:5]:
                    if not any(f["path"] == file_path for f in related_files):
                        related_files.append({
                            "path": file_path,
                            "reason": f"Part of {module['name']} module"
                        })
        
        return related_files[:20]  # Limit results
    
    async def _get_relevant_context(self, repository_id: str, question: str, analysis: Dict) -> str:
        """Get relevant code context for a question"""
        # Find related files
        related = await self.find_related_files(analysis, question)
        
        context_parts = []
        for file_info in related[:5]:  # Limit to 5 files
            try:
                content = await self.repo_service.get_file_content(repository_id, file_info["path"])
                context_parts.append(f"=== {file_info['path']} ===\n{content[:2000]}")
            except:
                pass
        
        return "\n\n".join(context_parts)
    
    async def _find_related_files_for_question(self, question: str, analysis: Dict) -> List[str]:
        """Find files related to a question"""
        # Extract keywords from question
        keywords = question.lower().split()
        stop_words = {"what", "how", "why", "does", "is", "the", "a", "an", "this", "that", "which", "where", "when", "can", "could", "would", "should"}
        keywords = [k for k in keywords if k not in stop_words and len(k) > 2]
        
        related_files = []
        
        for func in analysis.get("functionalities", []):
            func_name = func.get("name", "").lower()
            func_desc = func.get("description", "").lower()
            
            for keyword in keywords:
                if keyword in func_name or keyword in func_desc:
                    related_files.extend(func.get("files", [])[:3])
                    break
        
        return list(set(related_files))[:10]
    
    def _extract_code_snippets(self, text: str) -> List[Dict[str, str]]:
        """Extract code snippets from AI response"""
        snippets = []
        
        # Look for code blocks
        if "```" in text:
            parts = text.split("```")
            for i in range(1, len(parts), 2):
                if i < len(parts):
                    code_block = parts[i]
                    lines = code_block.split('\n')
                    
                    # First line might be the language
                    language = ""
                    code = code_block
                    
                    if lines and lines[0].strip() and not any(c in lines[0] for c in ['{', '(', '=', ';']):
                        language = lines[0].strip()
                        code = '\n'.join(lines[1:])
                    
                    snippets.append({
                        "language": language,
                        "code": code.strip()
                    })
        
        return snippets
