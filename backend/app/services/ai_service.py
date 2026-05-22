"""
AI Service - Handles AI-powered analysis and explanations
Supports: OpenAI, Ollama (local), Google Gemini
"""

import os
import json
import httpx
from typing import Dict, List, Any, Optional
from app.config import settings

# Try to import OpenAI
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Try to import Google Generative AI (new SDK)
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    # Fallback to deprecated package
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False


class AIService:
    """Service for AI-powered analysis - supports multiple providers (singleton)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.provider = settings.AI_PROVIDER.lower()
        self.client = None
        self.gemini_model = None
        
        # Initialize based on provider
        if self.provider == "openai" and OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
            print(f"AI Service initialized with OpenAI ({self.model})")
        
        elif self.provider == "gemini" and GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = None  # kept for backward compat checks
            self.model = settings.GEMINI_MODEL
            print(f"AI Service initialized with Google Gemini ({self.model})")
        
        elif self.provider == "ollama":
            self.ollama_url = settings.OLLAMA_BASE_URL
            self.model = settings.OLLAMA_MODEL
            print(f"AI Service initialized with Ollama ({self.model})")
        
        else:
            self.model = "none"
            print(f"AI Service: No provider configured or available")
    
    async def _call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """Make an AI API call based on configured provider"""
        
        if self.provider == "openai" and self.client:
            return await self._call_openai(system_prompt, user_prompt)
        
        elif self.provider == "gemini" and hasattr(self, 'gemini_client'):
            return await self._call_gemini(system_prompt, user_prompt)
        
        elif self.provider == "ollama":
            return await self._call_ollama(system_prompt, user_prompt)
        
        else:
            return self._get_fallback_response(user_prompt)
    
    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return f"OpenAI Error: {str(e)}"
    
    async def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Call Google Gemini API using the new google-genai SDK"""
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = self.gemini_client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return f"Gemini Error: {str(e)}"
    
    async def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """Call Ollama API (local)"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("message", {}).get("content", "No response from Ollama")
                else:
                    print(f"Ollama Error: {response.status_code} - {response.text}")
                    return self._get_ollama_not_running_message()
        except httpx.ConnectError:
            return self._get_ollama_not_running_message()
        except Exception as e:
            print(f"Ollama API Error: {e}")
            return self._get_ollama_not_running_message()
    
    def _get_ollama_not_running_message(self) -> str:
        """Message when Ollama is not running"""
        return """⚠️ **Ollama is not running or not installed.**

To use free local AI, please:

1. **Install Ollama** from https://ollama.com/download
2. **Start Ollama** (it runs in the background)
3. **Pull a model**: Open terminal and run:
   ```
   ollama pull llama3.2
   ```
4. **Retry** your question

Ollama is completely free and runs locally on your machine!

Alternative: Configure Google Gemini (free tier) in the .env file."""
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Get a fallback response when AI is not available"""
        return """**AI analysis is not available.**

Configure one of these AI providers in the `.env` file:

**Option 1: Ollama (FREE, Local)**
- Install from https://ollama.com/download
- Run: `ollama pull llama3.2`
- Set: `AI_PROVIDER=ollama`

**Option 2: Google Gemini (FREE tier)**
- Get API key from https://makersuite.google.com/app/apikey
- Set: `AI_PROVIDER=gemini`
- Set: `GEMINI_API_KEY=your-key`

**Option 3: OpenAI (Paid)**
- Get API key from https://platform.openai.com/api-keys
- Set: `AI_PROVIDER=openai`
- Set: `OPENAI_API_KEY=your-key`"""
    
    async def identify_functionalities(self, code_context: str, modules: List[Dict]) -> List[Dict[str, Any]]:
        """Identify functionalities in the codebase"""
        system_prompt = """You are an expert code analyst. Analyze the provided code and identify all major functionalities.
For each functionality, provide:
1. A clear name
2. A description of what it does
3. Related files
4. Core logic explanation

Return your response as a JSON array of objects with keys: name, description, files, core_logic"""
        
        module_summary = "\n".join([f"- {m['name']}: {m.get('file_count', 0)} files" for m in modules])
        
        user_prompt = f"""Analyze this codebase and identify all major functionalities:

MODULES:
{module_summary}

CODE CONTEXT:
{code_context[:15000]}

Return a JSON array of functionalities."""
        
        response = await self._call_ai(system_prompt, user_prompt)
        
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            
            return json.loads(json_str)
        except:
            return self._identify_functionalities_basic(modules)
    
    def _identify_functionalities_basic(self, modules: List[Dict]) -> List[Dict[str, Any]]:
        """Basic functionality identification without AI"""
        functionalities = []
        
        functionality_patterns = {
            "api": "API endpoints and route handling",
            "auth": "Authentication and authorization",
            "database": "Database operations and models",
            "models": "Data models and schemas",
            "services": "Business logic and services",
            "utils": "Utility functions and helpers",
            "components": "UI components",
            "views": "View layer and templates",
            "controllers": "Request controllers",
            "routes": "URL routing",
            "middleware": "Middleware functions",
            "tests": "Testing functionality",
            "config": "Configuration management"
        }
        
        for module in modules:
            module_name = module["name"].lower()
            for pattern, description in functionality_patterns.items():
                if pattern in module_name:
                    functionalities.append({
                        "name": module["name"],
                        "description": description,
                        "files": module.get("files", [])[:5],
                        "core_logic": f"Handles {description.lower()}"
                    })
                    break
            else:
                functionalities.append({
                    "name": module["name"],
                    "description": f"Module: {module['name']}",
                    "files": module.get("files", [])[:5],
                    "core_logic": "Functionality details require AI analysis"
                })
        
        return functionalities
    
    async def analyze_architecture(self, code_context: str, modules: List[Dict], tech_stack: List[str]) -> str:
        """Analyze and describe the architecture"""
        system_prompt = """You are a software architect. Analyze the provided code and describe:
1. The overall architecture pattern (MVC, microservices, monolith, etc.)
2. How components interact
3. Data flow
4. Key design decisions

Provide a clear, concise architectural overview."""
        
        module_summary = "\n".join([f"- {m['name']}" for m in modules])
        tech_summary = ", ".join(tech_stack) if tech_stack else "Not detected"
        
        user_prompt = f"""Analyze the architecture of this codebase:

TECHNOLOGY STACK: {tech_summary}

MODULES:
{module_summary}

CODE CONTEXT:
{code_context[:10000]}

Describe the architecture."""
        
        response = await self._call_ai(system_prompt, user_prompt)
        
        if "not available" in response.lower() or "ollama" in response.lower():
            return self._get_basic_architecture(modules, tech_stack)
        
        return response
    
    def _get_basic_architecture(self, modules: List[Dict], tech_stack: List[str]) -> str:
        """Get basic architecture description without AI"""
        module_names = [m["name"].lower() for m in modules]
        
        architecture = "## Architecture Overview\n\n"
        
        # Detect architecture pattern
        if any(name in module_names for name in ["controllers", "models", "views"]):
            architecture += "**Pattern:** MVC (Model-View-Controller)\n\n"
        elif any(name in module_names for name in ["services", "api", "handlers"]):
            architecture += "**Pattern:** Layered/Service-Oriented Architecture\n\n"
        elif any(name in module_names for name in ["components", "pages", "store"]):
            architecture += "**Pattern:** Component-Based Architecture\n\n"
        else:
            architecture += "**Pattern:** Custom/Modular Architecture\n\n"
        
        architecture += f"**Technology Stack:** {', '.join(tech_stack) if tech_stack else 'Not detected'}\n\n"
        
        architecture += "**Modules:**\n"
        for module in modules:
            architecture += f"- {module['name']}: {module.get('file_count', 0)} files\n"
        
        architecture += "\n*Detailed architecture analysis requires AI configuration.*"
        
        return architecture
    
    async def generate_summary(self, code_context: str, modules: List[Dict], functionalities: List[Dict]) -> str:
        """Generate a project summary"""
        system_prompt = """You are a technical writer. Create a concise but comprehensive summary of the project.
Include:
1. What the project does
2. Main features
3. Target users
4. Key technologies used

Keep it clear and professional."""
        
        func_summary = "\n".join([f"- {f['name']}: {f['description']}" for f in functionalities[:10]])
        
        user_prompt = f"""Summarize this project:

FUNCTIONALITIES:
{func_summary}

CODE CONTEXT:
{code_context[:8000]}

Write a project summary."""
        
        response = await self._call_ai(system_prompt, user_prompt)
        
        if "not available" in response.lower() or "ollama" in response.lower():
            return self._get_basic_summary(modules, functionalities)
        
        return response
    
    def _get_basic_summary(self, modules: List[Dict], functionalities: List[Dict]) -> str:
        """Get basic summary without AI"""
        summary = "## Project Summary\n\n"
        summary += "This project contains the following modules:\n\n"
        
        for module in modules[:10]:
            summary += f"- **{module['name']}**: {module.get('file_count', 0)} files\n"
        
        if functionalities:
            summary += "\n### Identified Functionalities:\n\n"
            for func in functionalities[:10]:
                summary += f"- **{func['name']}**: {func['description']}\n"
        
        summary += "\n*Detailed summary requires AI configuration.*"
        
        return summary
    
    async def explain_project(self, analysis: Dict) -> Dict[str, Any]:
        """Generate comprehensive project explanation"""
        system_prompt = """You are a senior developer explaining a project to a new team member.
Provide a comprehensive explanation covering:
1. WHAT: What the project does and its purpose
2. WHY: Why it was developed, what problem it solves
3. HOW: How it works technically
4. Architecture: High-level architecture overview
5. Workflow: Main workflow/process flow

Return as JSON with keys: what, why, how, architecture, workflow, functionalities"""
        
        context = f"""
PROJECT: {analysis.get('repository_name', 'Unknown')}
TECH STACK: {', '.join(analysis.get('tech_stack', []))}
MODULES: {', '.join([m['name'] for m in analysis.get('modules', [])])}
FUNCTIONALITIES: {json.dumps(analysis.get('functionalities', [])[:5])}
ARCHITECTURE: {analysis.get('architecture', '')}
SUMMARY: {analysis.get('summary', '')}
"""
        
        response = await self._call_ai(system_prompt, f"Explain this project:\n{context}")
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            
            return json.loads(json_str)
        except:
            return {
                "what": response[:500] if response else "AI explanation unavailable",
                "why": "Configure AI provider for detailed explanation",
                "how": "Configure AI provider for detailed explanation",
                "architecture": analysis.get("architecture", ""),
                "workflow": "Configure AI provider for workflow details",
                "functionalities": analysis.get("functionalities", [])
            }
    
    def _get_basic_explanation(self, analysis: Dict) -> Dict[str, Any]:
        """Get basic explanation without AI"""
        return {
            "what": f"This is a software project named '{analysis.get('repository_name', 'Unknown')}' containing {analysis.get('structure', {}).get('total_files', 0)} files.",
            "why": "Detailed purpose analysis requires AI configuration.",
            "how": f"The project uses: {', '.join(analysis.get('tech_stack', ['Unknown']))}",
            "architecture": analysis.get("architecture", "Architecture analysis requires AI configuration."),
            "workflow": "Workflow analysis requires AI configuration.",
            "functionalities": [{"name": f["name"], "explanation": f["description"]} for f in analysis.get("functionalities", [])]
        }
    
    async def answer_question(self, question: str, analysis: Dict, code_context: str = "", conversation_history: List = None) -> str:
        """Answer a question about the repository"""
        system_prompt = f"""You are an AI assistant that helps developers understand a codebase.
You have knowledge about this project:
- Name: {analysis.get('repository_name', 'Unknown')}
- Tech Stack: {', '.join(analysis.get('tech_stack', []))}
- Modules: {', '.join([m['name'] for m in analysis.get('modules', [])])}

Answer questions accurately based on the provided context. If you don't know something, say so."""
        
        context = f"""
PROJECT SUMMARY: {analysis.get('summary', '')}
ARCHITECTURE: {analysis.get('architecture', '')}
FUNCTIONALITIES: {json.dumps(analysis.get('functionalities', [])[:10])}
"""
        
        user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
        
        # For OpenAI with conversation history
        if self.provider == "openai" and self.client and conversation_history:
            try:
                messages = [{"role": "system", "content": system_prompt}]
                for msg in conversation_history[-5:]:
                    messages.append({"role": msg.role, "content": msg.content})
                messages.append({"role": "user", "content": user_prompt})
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Error generating response: {str(e)}"
        
        # For other providers
        return await self._call_ai(system_prompt, user_prompt)
    
    async def explain_functionality_detailed(self, functionality: Dict, code_files: Dict[str, str], analysis: Dict) -> Dict[str, Any]:
        """
        Provide a detailed line-by-line explanation of a functionality.
        
        Args:
            functionality: The functionality details (name, description, files)
            code_files: Dict mapping file paths to their content
            analysis: The full analysis result for context
        
        Returns:
            Detailed explanation with line-by-line breakdown
        """
        system_prompt = """You are an expert code educator. Your task is to explain code functionality in extreme detail, line by line.

For each code file provided, you MUST:
1. Explain the PURPOSE of the entire file
2. Go through EVERY significant line and explain:
   - WHAT the line does
   - WHY it's written this way
   - HOW it connects to other parts of the code
3. Explain any patterns, design choices, or best practices used
4. Highlight any potential issues or improvements

Your explanation should be:
- Detailed enough for a beginner to understand
- Technical enough for an experienced developer to learn something
- Structured with clear sections for each file and code block

Return your response as JSON with this structure:
{
    "overview": "High-level explanation of what this functionality does",
    "purpose": "Why this functionality exists and what problem it solves",
    "how_it_works": "Step-by-step explanation of the flow",
    "file_explanations": [
        {
            "file_path": "path/to/file",
            "file_purpose": "What this file does",
            "code_blocks": [
                {
                    "lines": "1-10",
                    "code": "the actual code",
                    "explanation": "Detailed line-by-line explanation",
                    "why": "Why this code is written this way",
                    "concepts": ["concept1", "concept2"]
                }
            ],
            "key_takeaways": ["takeaway1", "takeaway2"]
        }
    ],
    "data_flow": "How data flows through this functionality",
    "dependencies": ["What this functionality depends on"],
    "patterns_used": ["Design patterns or coding patterns identified"],
    "best_practices": ["Best practices demonstrated in this code"],
    "potential_improvements": ["Suggestions for improvement"]
}"""

        # Build the code context
        code_context = ""
        for file_path, content in code_files.items():
            # Add line numbers to the code
            numbered_lines = []
            for i, line in enumerate(content.split('\n'), 1):
                numbered_lines.append(f"{i:4d} | {line}")
            numbered_content = '\n'.join(numbered_lines)
            code_context += f"\n\n=== FILE: {file_path} ===\n{numbered_content}"
        
        user_prompt = f"""Analyze and explain this functionality in extreme detail:

FUNCTIONALITY NAME: {functionality.get('name', 'Unknown')}
DESCRIPTION: {functionality.get('description', 'No description')}
CORE LOGIC: {functionality.get('core_logic', 'No core logic description')}

PROJECT CONTEXT:
- Tech Stack: {', '.join(analysis.get('tech_stack', []))}
- This is part of: {analysis.get('repository_name', 'Unknown')}

CODE FILES TO EXPLAIN:
{code_context}

Provide an extremely detailed, line-by-line explanation. For each significant line or block, explain WHAT it does, WHY it's done this way, and HOW it fits into the bigger picture.

Remember to return valid JSON."""

        response = await self._call_ai(system_prompt, user_prompt)
        
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            
            return json.loads(json_str)
        except Exception as e:
            # Return a structured fallback response
            return self._get_fallback_detailed_explanation(functionality, code_files)
    
    def _get_fallback_detailed_explanation(self, functionality: Dict, code_files: Dict[str, str]) -> Dict[str, Any]:
        """Generate a basic explanation when AI is not available"""
        file_explanations = []
        
        for file_path, content in code_files.items():
            lines = content.split('\n')
            code_blocks = []
            
            # Break code into chunks of ~10 lines
            chunk_size = 10
            for i in range(0, len(lines), chunk_size):
                chunk = lines[i:i + chunk_size]
                code_blocks.append({
                    "lines": f"{i+1}-{min(i + chunk_size, len(lines))}",
                    "code": '\n'.join(chunk),
                    "explanation": "AI analysis required for detailed explanation. Configure an AI provider in the .env file.",
                    "why": "Configure AI for detailed reasoning",
                    "concepts": []
                })
            
            file_explanations.append({
                "file_path": file_path,
                "file_purpose": f"Part of the {functionality.get('name', 'unknown')} functionality",
                "code_blocks": code_blocks[:5],  # Limit blocks
                "key_takeaways": ["Configure AI provider for detailed analysis"]
            })
        
        return {
            "overview": functionality.get('description', 'No description available'),
            "purpose": functionality.get('core_logic', 'AI analysis required'),
            "how_it_works": "Configure an AI provider (Ollama, Gemini, or OpenAI) for detailed explanations.",
            "file_explanations": file_explanations,
            "data_flow": "AI analysis required",
            "dependencies": [],
            "patterns_used": [],
            "best_practices": [],
            "potential_improvements": ["Configure AI for detailed code review"]
        }
    
    async def explain_code_block(self, code: str, language: str, context: str = "") -> Dict[str, Any]:
        """
        Explain a specific code block line by line.
        
        Args:
            code: The code to explain
            language: Programming language
            context: Additional context about where this code is used
        
        Returns:
            Detailed line-by-line explanation
        """
        system_prompt = f"""You are an expert code educator specializing in {language}.
Explain the provided code LINE BY LINE in extreme detail.

For EACH line, provide:
1. What the line does (technically)
2. Why it's written this way
3. Any important concepts or patterns it demonstrates
4. How it connects to other lines

Return JSON format:
{{
    "summary": "Brief summary of what the code does",
    "language": "{language}",
    "line_explanations": [
        {{
            "line_number": 1,
            "code": "actual code on this line",
            "what": "What this line does",
            "why": "Why it's written this way",
            "concepts": ["relevant concepts"],
            "notes": "Any additional notes"
        }}
    ],
    "overall_flow": "How the code flows from start to end",
    "key_concepts": ["Important concepts used in this code"],
    "common_pitfalls": ["Things to watch out for"]
}}"""

        # Add line numbers
        numbered_lines = []
        for i, line in enumerate(code.split('\n'), 1):
            numbered_lines.append(f"{i:4d} | {line}")
        numbered_code = '\n'.join(numbered_lines)

        user_prompt = f"""Explain this {language} code line by line:

{numbered_code}

{f'Context: {context}' if context else ''}

Provide detailed explanation for EVERY line. Return valid JSON."""

        response = await self._call_ai(system_prompt, user_prompt)
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            
            return json.loads(json_str)
        except:
            # Fallback response
            lines = code.split('\n')
            return {
                "summary": "AI analysis required for detailed explanation",
                "language": language,
                "line_explanations": [
                    {
                        "line_number": i + 1,
                        "code": line,
                        "what": "Configure AI for explanation",
                        "why": "AI provider needed",
                        "concepts": [],
                        "notes": ""
                    }
                    for i, line in enumerate(lines) if line.strip()
                ],
                "overall_flow": "Configure AI provider for detailed flow analysis",
                "key_concepts": [],
                "common_pitfalls": []
            }
