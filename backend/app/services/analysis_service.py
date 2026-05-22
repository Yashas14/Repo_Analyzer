"""
Analysis Service - Handles repository analysis
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from app.config import settings
from app.services.repository_service import RepositoryService
from app.services.ai_service import AIService
from app.models.schemas import (
    AnalysisResult, RepositoryStructure, ModuleInfo, 
    FunctionalityInfo, FileInfo, DependencyInfo
)


class AnalysisService:
    """Service for analyzing repositories"""
    
    def __init__(self):
        self.repo_service = RepositoryService()
        self.ai_service = AIService()
        self.analysis_cache = {}
    
    async def repository_exists(self, repo_id: str) -> bool:
        """Check if a repository exists"""
        repo_path = self.repo_service._get_repo_path(repo_id)
        return repo_path is not None
    
    async def analyze_repository(self, repo_id: str) -> Dict[str, Any]:
        """Perform complete analysis of a repository"""
        repo_path = self.repo_service._get_repo_path(repo_id)
        if not repo_path:
            raise FileNotFoundError("Repository not found")
        
        metadata = self.repo_service._load_metadata(repo_path)
        source_path = metadata.get("path", os.path.join(repo_path, "source"))
        
        # Gather repository information
        structure = await self._analyze_structure(source_path, metadata.get("name", "Unknown"))
        modules = await self._identify_modules(source_path)
        dependencies = await self._extract_dependencies(source_path)
        tech_stack = await self._identify_tech_stack(source_path, dependencies)
        
        # Get file contents for AI analysis
        code_context = await self._gather_code_context(source_path)
        
        # AI-powered analysis
        functionalities = await self.ai_service.identify_functionalities(code_context, modules)
        architecture = await self.ai_service.analyze_architecture(code_context, modules, tech_stack)
        summary = await self.ai_service.generate_summary(code_context, modules, functionalities)
        
        # Build analysis result
        analysis_result = {
            "repository_id": repo_id,
            "repository_name": metadata.get("name", "Unknown"),
            "analysis_date": datetime.now().isoformat(),
            "structure": structure,
            "modules": modules,
            "functionalities": functionalities,
            "dependencies": dependencies,
            "tech_stack": tech_stack,
            "architecture": architecture,
            "summary": summary
        }
        
        # Save analysis result
        self._save_analysis(repo_path, analysis_result)
        self.analysis_cache[repo_id] = analysis_result
        
        return analysis_result
    
    async def get_analysis_status(self, repo_id: str) -> Dict[str, Any]:
        """Get the status of an analysis"""
        repo_path = self.repo_service._get_repo_path(repo_id)
        if not repo_path:
            raise FileNotFoundError("Repository not found")
        
        analysis_path = os.path.join(repo_path, "analysis_result.json")
        
        if os.path.exists(analysis_path):
            return {"status": "completed", "repository_id": repo_id}
        elif repo_id in self.analysis_cache:
            return {"status": "in_progress", "repository_id": repo_id}
        else:
            return {"status": "not_started", "repository_id": repo_id}
    
    async def get_analysis_result(self, repo_id: str) -> Dict[str, Any]:
        """Get the analysis result for a repository"""
        # Check cache first
        if repo_id in self.analysis_cache:
            return self.analysis_cache[repo_id]
        
        # Load from file
        repo_path = self.repo_service._get_repo_path(repo_id)
        if not repo_path:
            raise FileNotFoundError("Repository not found")
        
        analysis_path = os.path.join(repo_path, "analysis_result.json")
        
        if not os.path.exists(analysis_path):
            raise FileNotFoundError("Analysis not found. Please run analysis first.")
        
        with open(analysis_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        self.analysis_cache[repo_id] = result
        return result
    
    async def get_functionalities(self, repo_id: str) -> List[Dict[str, Any]]:
        """Get functionalities from analysis"""
        result = await self.get_analysis_result(repo_id)
        return result.get("functionalities", [])
    
    async def get_modules(self, repo_id: str) -> List[Dict[str, Any]]:
        """Get modules from analysis"""
        result = await self.get_analysis_result(repo_id)
        return result.get("modules", [])
    
    async def get_architecture(self, repo_id: str) -> str:
        """Get architecture from analysis"""
        result = await self.get_analysis_result(repo_id)
        return result.get("architecture", "")
    
    async def get_tech_stack(self, repo_id: str) -> List[str]:
        """Get tech stack from analysis"""
        result = await self.get_analysis_result(repo_id)
        return result.get("tech_stack", [])
    
    async def get_dependencies(self, repo_id: str) -> List[Dict[str, Any]]:
        """Get dependencies from analysis"""
        result = await self.get_analysis_result(repo_id)
        return result.get("dependencies", [])
    
    async def get_repository_path(self, repo_id: str) -> str:
        """Get the source path for a repository"""
        repo_path = self.repo_service._get_repo_path(repo_id)
        if not repo_path:
            raise FileNotFoundError("Repository not found")
        
        metadata = self.repo_service._load_metadata(repo_path)
        source_path = metadata.get("path", os.path.join(repo_path, "source"))
        
        return source_path
    
    def _save_analysis(self, repo_path: str, analysis: Dict[str, Any]):
        """Save analysis result to file"""
        analysis_path = os.path.join(repo_path, "analysis_result.json")
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
    
    async def _analyze_structure(self, source_path: str, repo_name: str) -> Dict[str, Any]:
        """Analyze the repository structure"""
        total_files = 0
        total_lines = 0
        languages = {}
        files = []
        
        language_map = {
            # Python
            ".py": "Python", ".pyw": "Python", ".pyx": "Cython", ".ipynb": "Jupyter Notebook",
            # JavaScript/TypeScript
            ".js": "JavaScript", ".jsx": "React JSX", ".mjs": "JavaScript (ESM)", ".cjs": "JavaScript (CJS)",
            ".ts": "TypeScript", ".tsx": "React TSX", ".mts": "TypeScript (ESM)", ".cts": "TypeScript (CJS)",
            # Java/JVM
            ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin Script",
            ".scala": "Scala", ".sc": "Scala", ".groovy": "Groovy", ".gradle": "Gradle",
            ".clj": "Clojure", ".cljs": "ClojureScript",
            # C/C++/Objective-C
            ".c": "C", ".h": "C Header", ".cpp": "C++", ".hpp": "C++ Header",
            ".cc": "C++", ".hh": "C++ Header", ".cxx": "C++", ".hxx": "C++ Header",
            ".m": "Objective-C", ".mm": "Objective-C++",
            # C#/F#/.NET
            ".cs": "C#", ".csx": "C# Script", ".fs": "F#", ".fsx": "F# Script",
            ".vb": "Visual Basic", ".xaml": "XAML",
            # Go
            ".go": "Go",
            # Rust
            ".rs": "Rust",
            # Ruby
            ".rb": "Ruby", ".erb": "ERB", ".rake": "Rake", ".gemspec": "Gemspec",
            # PHP
            ".php": "PHP", ".phtml": "PHP",
            # Swift
            ".swift": "Swift",
            # Perl
            ".pl": "Perl", ".pm": "Perl Module",
            # Lua
            ".lua": "Lua",
            # R
            ".r": "R", ".R": "R", ".rmd": "R Markdown", ".Rmd": "R Markdown",
            # Julia
            ".jl": "Julia",
            # Haskell
            ".hs": "Haskell", ".lhs": "Literate Haskell",
            # Elixir/Erlang
            ".ex": "Elixir", ".exs": "Elixir Script", ".erl": "Erlang", ".hrl": "Erlang Header",
            # Dart
            ".dart": "Dart",
            # COBOL
            ".cob": "COBOL", ".cbl": "COBOL", ".cobol": "COBOL",
            # Fortran
            ".f": "Fortran", ".for": "Fortran", ".f90": "Fortran 90", ".f95": "Fortran 95",
            # Assembly
            ".asm": "Assembly", ".s": "Assembly", ".S": "Assembly",
            # Shell
            ".sh": "Shell", ".bash": "Bash", ".zsh": "Zsh", ".fish": "Fish",
            ".ps1": "PowerShell", ".psm1": "PowerShell Module", ".bat": "Batch", ".cmd": "Batch",
            # Web
            ".html": "HTML", ".htm": "HTML", ".xhtml": "XHTML",
            ".css": "CSS", ".scss": "SCSS", ".sass": "Sass", ".less": "Less", ".styl": "Stylus",
            ".vue": "Vue", ".svelte": "Svelte", ".astro": "Astro",
            # Data/Config
            ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
            ".xml": "XML", ".xsl": "XSLT", ".ini": "INI", ".cfg": "Config",
            # Database
            ".sql": "SQL", ".pgsql": "PostgreSQL", ".mysql": "MySQL", ".plsql": "PL/SQL",
            # Documentation
            ".md": "Markdown", ".markdown": "Markdown", ".rst": "reStructuredText", ".txt": "Text",
            ".tex": "LaTeX", ".org": "Org Mode",
            # DevOps
            ".dockerfile": "Dockerfile", ".tf": "Terraform", ".tfvars": "Terraform Vars",
            ".hcl": "HCL", ".jenkinsfile": "Jenkinsfile",
            # GraphQL/API
            ".graphql": "GraphQL", ".gql": "GraphQL", ".proto": "Protocol Buffers",
            # Blockchain
            ".sol": "Solidity", ".vy": "Vyper",
            # Other Languages
            ".nim": "Nim", ".zig": "Zig", ".v": "V", ".d": "D", ".cr": "Crystal",
            ".ml": "OCaml", ".mli": "OCaml Interface", ".elm": "Elm", ".purs": "PureScript",
            ".rkt": "Racket", ".scm": "Scheme", ".lisp": "Lisp", ".cl": "Common Lisp",
            ".tcl": "Tcl", ".awk": "AWK",
            # Hardware Description
            ".vhd": "VHDL", ".vhdl": "VHDL", ".sv": "SystemVerilog", ".svh": "SystemVerilog Header"
        }
        
        for root, dirs, filenames in os.walk(source_path):
            dirs[:] = [d for d in dirs if not self.repo_service._should_ignore(d)]
            
            for filename in filenames:
                if self.repo_service._should_ignore(filename):
                    continue
                
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, source_path)
                _, ext = os.path.splitext(filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        line_count = len(content.splitlines())
                except:
                    line_count = 0
                
                total_files += 1
                total_lines += line_count
                
                # Track languages
                if ext in language_map:
                    lang = language_map[ext]
                    languages[lang] = languages.get(lang, 0) + 1
                
                files.append({
                    "path": relative_path,
                    "name": filename,
                    "extension": ext,
                    "size": os.path.getsize(file_path),
                    "lines": line_count
                })
        
        return {
            "name": repo_name,
            "path": source_path,
            "total_files": total_files,
            "total_lines": total_lines,
            "languages": languages,
            "files": files
        }
    
    async def _identify_modules(self, source_path: str) -> List[Dict[str, Any]]:
        """Identify modules/components in the repository"""
        modules = []
        
        # Common module patterns
        module_indicators = [
            "src", "lib", "app", "api", "services", "controllers", "models",
            "views", "components", "utils", "helpers", "core", "modules",
            "packages", "features", "pages", "routes", "handlers"
        ]
        
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if not self.repo_service._should_ignore(d)]
            relative_root = os.path.relpath(root, source_path)
            
            for dir_name in dirs:
                if dir_name.lower() in module_indicators or self._has_init_file(os.path.join(root, dir_name)):
                    module_path = os.path.join(relative_root, dir_name) if relative_root != "." else dir_name
                    module_files = self._get_module_files(os.path.join(root, dir_name), source_path)
                    
                    modules.append({
                        "name": dir_name,
                        "path": module_path,
                        "files": module_files,
                        "file_count": len(module_files)
                    })
        
        # If no modules found, treat top-level as modules
        if not modules:
            for item in os.listdir(source_path):
                item_path = os.path.join(source_path, item)
                if os.path.isdir(item_path) and not self.repo_service._should_ignore(item):
                    module_files = self._get_module_files(item_path, source_path)
                    modules.append({
                        "name": item,
                        "path": item,
                        "files": module_files,
                        "file_count": len(module_files)
                    })
        
        return modules
    
    def _has_init_file(self, path: str) -> bool:
        """Check if directory has an __init__.py file (Python module)"""
        return os.path.exists(os.path.join(path, "__init__.py"))
    
    def _get_module_files(self, module_path: str, source_path: str) -> List[str]:
        """Get files within a module"""
        files = []
        for root, dirs, filenames in os.walk(module_path):
            dirs[:] = [d for d in dirs if not self.repo_service._should_ignore(d)]
            for filename in filenames:
                if not self.repo_service._should_ignore(filename):
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, source_path)
                    files.append(relative_path)
        return files
    
    async def _extract_dependencies(self, source_path: str) -> List[Dict[str, Any]]:
        """Extract dependencies from package files for any programming language"""
        dependencies = []
        
        # Check for package.json (Node.js/JavaScript/TypeScript)
        package_json = os.path.join(source_path, "package.json")
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    pkg = json.load(f)
                
                for name, version in pkg.get("dependencies", {}).items():
                    dependencies.append({"name": name, "version": version, "type": "runtime", "language": "JavaScript/TypeScript"})
                
                for name, version in pkg.get("devDependencies", {}).items():
                    dependencies.append({"name": name, "version": version, "type": "dev", "language": "JavaScript/TypeScript"})
            except:
                pass
        
        # Check for requirements.txt (Python)
        requirements_txt = os.path.join(source_path, "requirements.txt")
        if os.path.exists(requirements_txt):
            try:
                with open(requirements_txt, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('-'):
                            name = line.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0].strip()
                            version = "latest"
                            if '==' in line:
                                version = line.split('==')[1].split()[0]
                            dependencies.append({"name": name, "version": version, "type": "runtime", "language": "Python"})
            except:
                pass
        
        # Check for pyproject.toml (Python - Poetry/PEP 621)
        pyproject_toml = os.path.join(source_path, "pyproject.toml")
        if os.path.exists(pyproject_toml):
            try:
                with open(pyproject_toml, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Simple parsing for dependencies
                import re
                # Poetry style
                poetry_deps = re.findall(r'^\s*(\w[\w-]*)\s*=\s*["\']?([^"\'\n]+)', content, re.MULTILINE)
                for name, version in poetry_deps:
                    if name not in ['python', 'name', 'version', 'description', 'authors']:
                        dependencies.append({"name": name, "version": version, "type": "runtime", "language": "Python"})
            except:
                pass
        
        # Check for Pipfile (Python - Pipenv)
        pipfile = os.path.join(source_path, "Pipfile")
        if os.path.exists(pipfile):
            try:
                with open(pipfile, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                deps = re.findall(r'^\s*(\w[\w-]*)\s*=', content, re.MULTILINE)
                for name in deps:
                    if name not in ['python_version', 'url', 'verify_ssl', 'name']:
                        dependencies.append({"name": name, "version": "latest", "type": "runtime", "language": "Python"})
            except:
                pass
        
        # Check for pom.xml (Java/Maven)
        pom_xml = os.path.join(source_path, "pom.xml")
        if os.path.exists(pom_xml):
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(pom_xml)
                root = tree.getroot()
                # Handle both with and without namespace
                ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                
                for dep in root.findall('.//maven:dependency', ns) or root.findall('.//dependency'):
                    artifact_id = dep.find('maven:artifactId', ns) or dep.find('artifactId')
                    group_id = dep.find('maven:groupId', ns) or dep.find('groupId')
                    version = dep.find('maven:version', ns) or dep.find('version')
                    if artifact_id is not None:
                        name = f"{group_id.text}:{artifact_id.text}" if group_id is not None else artifact_id.text
                        dependencies.append({
                            "name": name,
                            "version": version.text if version is not None else "latest",
                            "type": "runtime",
                            "language": "Java"
                        })
            except:
                pass
        
        # Check for build.gradle / build.gradle.kts (Java/Kotlin - Gradle)
        for gradle_file in ["build.gradle", "build.gradle.kts"]:
            gradle_path = os.path.join(source_path, gradle_file)
            if os.path.exists(gradle_path):
                try:
                    with open(gradle_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    import re
                    # Match implementation, api, compile, etc.
                    deps = re.findall(r'(?:implementation|api|compile|runtimeOnly|testImplementation)\s*[(\s]["\']([^"\']+)["\']', content)
                    for dep in deps:
                        parts = dep.split(':')
                        name = ':'.join(parts[:2]) if len(parts) >= 2 else dep
                        version = parts[2] if len(parts) >= 3 else "latest"
                        dependencies.append({"name": name, "version": version, "type": "runtime", "language": "Java/Kotlin"})
                except:
                    pass
        
        # Check for go.mod (Go)
        go_mod = os.path.join(source_path, "go.mod")
        if os.path.exists(go_mod):
            try:
                with open(go_mod, 'r', encoding='utf-8') as f:
                    in_require = False
                    for line in f:
                        line = line.strip()
                        if line.startswith('require ('):
                            in_require = True
                            continue
                        if in_require and line == ')':
                            in_require = False
                            continue
                        if in_require or line.startswith('require '):
                            parts = line.replace('require ', '').strip().split()
                            if len(parts) >= 2 and '/' in parts[0]:
                                dependencies.append({
                                    "name": parts[0],
                                    "version": parts[1],
                                    "type": "runtime",
                                    "language": "Go"
                                })
            except:
                pass
        
        # Check for Cargo.toml (Rust)
        cargo_toml = os.path.join(source_path, "Cargo.toml")
        if os.path.exists(cargo_toml):
            try:
                with open(cargo_toml, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                # Match [dependencies] section
                deps_section = re.search(r'\[dependencies\](.*?)(?=\[|\Z)', content, re.DOTALL)
                if deps_section:
                    deps = re.findall(r'^(\w[\w-]*)\s*=\s*["\']?([^"\'\n{]+)', deps_section.group(1), re.MULTILINE)
                    for name, version in deps:
                        dependencies.append({"name": name, "version": version.strip(), "type": "runtime", "language": "Rust"})
            except:
                pass
        
        # Check for Gemfile (Ruby)
        gemfile = os.path.join(source_path, "Gemfile")
        if os.path.exists(gemfile):
            try:
                with open(gemfile, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                gems = re.findall(r"gem\s+['\"]([^'\"]+)['\"](?:,\s*['\"]([^'\"]*)['\"])?", content)
                for gem in gems:
                    dependencies.append({
                        "name": gem[0],
                        "version": gem[1] if gem[1] else "latest",
                        "type": "runtime",
                        "language": "Ruby"
                    })
            except:
                pass
        
        # Check for composer.json (PHP)
        composer_json = os.path.join(source_path, "composer.json")
        if os.path.exists(composer_json):
            try:
                with open(composer_json, 'r', encoding='utf-8') as f:
                    pkg = json.load(f)
                
                for name, version in pkg.get("require", {}).items():
                    if name != 'php':
                        dependencies.append({"name": name, "version": version, "type": "runtime", "language": "PHP"})
                
                for name, version in pkg.get("require-dev", {}).items():
                    dependencies.append({"name": name, "version": version, "type": "dev", "language": "PHP"})
            except:
                pass
        
        # Check for pubspec.yaml (Dart/Flutter)
        pubspec_yaml = os.path.join(source_path, "pubspec.yaml")
        if os.path.exists(pubspec_yaml):
            try:
                with open(pubspec_yaml, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                # Simple YAML parsing for dependencies
                deps_section = re.search(r'dependencies:(.*?)(?=dev_dependencies:|dependency_overrides:|flutter:|$)', content, re.DOTALL)
                if deps_section:
                    deps = re.findall(r'^\s+(\w[\w_]*)\s*:\s*[\^]?([^\n#]+)?', deps_section.group(1), re.MULTILINE)
                    for name, version in deps:
                        if name not in ['flutter', 'sdk']:
                            dependencies.append({"name": name, "version": version.strip() if version else "latest", "type": "runtime", "language": "Dart"})
            except:
                pass
        
        # Check for Package.swift (Swift)
        package_swift = os.path.join(source_path, "Package.swift")
        if os.path.exists(package_swift):
            try:
                with open(package_swift, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                deps = re.findall(r'\.package\s*\(\s*url:\s*["\']([^"\']+)["\']', content)
                for dep in deps:
                    name = dep.split('/')[-1].replace('.git', '')
                    dependencies.append({"name": name, "version": "latest", "type": "runtime", "language": "Swift"})
            except:
                pass
        
        # Check for .csproj / .fsproj (C#/F# - .NET)
        for ext in ['.csproj', '.fsproj', '.vbproj']:
            for root, dirs, files in os.walk(source_path):
                for filename in files:
                    if filename.endswith(ext):
                        proj_path = os.path.join(root, filename)
                        try:
                            import xml.etree.ElementTree as ET
                            tree = ET.parse(proj_path)
                            proj_root = tree.getroot()
                            for pkg_ref in proj_root.findall('.//PackageReference'):
                                name = pkg_ref.get('Include')
                                version = pkg_ref.get('Version', 'latest')
                                if name:
                                    dependencies.append({"name": name, "version": version, "type": "runtime", "language": ".NET"})
                        except:
                            pass
                break  # Only check first level
        
        # Check for mix.exs (Elixir)
        mix_exs = os.path.join(source_path, "mix.exs")
        if os.path.exists(mix_exs):
            try:
                with open(mix_exs, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                deps = re.findall(r'\{:(\w+),\s*["\']([^"\']+)["\']', content)
                for name, version in deps:
                    dependencies.append({"name": name, "version": version, "type": "runtime", "language": "Elixir"})
            except:
                pass
        
        # Check for rebar.config (Erlang)
        rebar_config = os.path.join(source_path, "rebar.config")
        if os.path.exists(rebar_config):
            try:
                with open(rebar_config, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                deps = re.findall(r'\{(\w+),\s*["\']([^"\']+)["\']', content)
                for name, version in deps:
                    dependencies.append({"name": name, "version": version, "type": "runtime", "language": "Erlang"})
            except:
                pass
        
        # Check for cabal file (Haskell)
        for root, dirs, files in os.walk(source_path):
            for filename in files:
                if filename.endswith('.cabal'):
                    cabal_path = os.path.join(root, filename)
                    try:
                        with open(cabal_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        import re
                        deps = re.findall(r'build-depends:\s*([^\n]+)', content)
                        for dep_line in deps:
                            for dep in dep_line.split(','):
                                dep = dep.strip()
                                if dep:
                                    name = dep.split()[0]
                                    dependencies.append({"name": name, "version": "latest", "type": "runtime", "language": "Haskell"})
                    except:
                        pass
            break
        
        # Check for Project.toml (Julia)
        project_toml = os.path.join(source_path, "Project.toml")
        if os.path.exists(project_toml):
            try:
                with open(project_toml, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                deps_section = re.search(r'\[deps\](.*?)(?=\[|\Z)', content, re.DOTALL)
                if deps_section:
                    deps = re.findall(r'^(\w+)\s*=', deps_section.group(1), re.MULTILINE)
                    for name in deps:
                        dependencies.append({"name": name, "version": "latest", "type": "runtime", "language": "Julia"})
            except:
                pass
        
        # Check for DESCRIPTION (R)
        description_file = os.path.join(source_path, "DESCRIPTION")
        if os.path.exists(description_file):
            try:
                with open(description_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                imports = re.search(r'Imports:\s*([^\n]+(?:\n\s+[^\n]+)*)', content)
                depends = re.search(r'Depends:\s*([^\n]+(?:\n\s+[^\n]+)*)', content)
                for match in [imports, depends]:
                    if match:
                        deps = re.findall(r'(\w+)', match.group(1))
                        for name in deps:
                            if name not in ['R']:
                                dependencies.append({"name": name, "version": "latest", "type": "runtime", "language": "R"})
            except:
                pass
        
        return dependencies
    
    async def _identify_tech_stack(self, source_path: str, dependencies: List[Dict]) -> List[str]:
        """Identify the technology stack for any programming language"""
        tech_stack = set()
        
        # Check for specific files that indicate technologies
        file_tech_map = {
            # JavaScript/TypeScript
            "package.json": "Node.js",
            "package-lock.json": "npm",
            "yarn.lock": "Yarn",
            "pnpm-lock.yaml": "pnpm",
            "bun.lockb": "Bun",
            "deno.json": "Deno",
            "deno.jsonc": "Deno",
            # Python
            "requirements.txt": "Python",
            "pyproject.toml": "Python",
            "setup.py": "Python",
            "Pipfile": "Pipenv",
            "poetry.lock": "Poetry",
            "conda.yaml": "Conda",
            "environment.yml": "Conda",
            # Ruby
            "Gemfile": "Ruby",
            "Gemfile.lock": "Bundler",
            "Rakefile": "Rake",
            # Java/JVM
            "pom.xml": "Maven",
            "build.gradle": "Gradle",
            "build.gradle.kts": "Gradle (Kotlin DSL)",
            "gradlew": "Gradle",
            "mvnw": "Maven Wrapper",
            "build.sbt": "SBT (Scala)",
            "project.clj": "Leiningen (Clojure)",
            # .NET
            "*.csproj": "C#/.NET",
            "*.fsproj": "F#/.NET",
            "*.sln": ".NET Solution",
            "nuget.config": "NuGet",
            "global.json": ".NET",
            # Rust
            "Cargo.toml": "Rust/Cargo",
            "Cargo.lock": "Rust/Cargo",
            # Go
            "go.mod": "Go",
            "go.sum": "Go",
            # PHP
            "composer.json": "PHP/Composer",
            "composer.lock": "PHP/Composer",
            # Swift
            "Package.swift": "Swift Package Manager",
            "Podfile": "CocoaPods",
            "Cartfile": "Carthage",
            # Dart/Flutter
            "pubspec.yaml": "Dart/Flutter",
            "pubspec.lock": "Dart/Flutter",
            # Elixir
            "mix.exs": "Elixir/Mix",
            "mix.lock": "Elixir/Mix",
            # Erlang
            "rebar.config": "Erlang/Rebar",
            # Haskell
            "stack.yaml": "Haskell Stack",
            "cabal.project": "Cabal",
            # Julia
            "Project.toml": "Julia",
            "Manifest.toml": "Julia",
            # R
            "DESCRIPTION": "R Package",
            "renv.lock": "renv (R)",
            # Nim
            "nimble": "Nimble (Nim)",
            # Zig
            "build.zig": "Zig",
            # DevOps/Infrastructure
            "Dockerfile": "Docker",
            "docker-compose.yml": "Docker Compose",
            "docker-compose.yaml": "Docker Compose",
            "Containerfile": "Podman/Docker",
            ".gitlab-ci.yml": "GitLab CI/CD",
            ".github": "GitHub Actions",
            "Jenkinsfile": "Jenkins",
            "azure-pipelines.yml": "Azure Pipelines",
            ".circleci": "CircleCI",
            "bitbucket-pipelines.yml": "Bitbucket Pipelines",
            ".travis.yml": "Travis CI",
            "appveyor.yml": "AppVeyor",
            # IaC
            "main.tf": "Terraform",
            "terraform.tfvars": "Terraform",
            "pulumi.yaml": "Pulumi",
            "serverless.yml": "Serverless Framework",
            "sam.yaml": "AWS SAM",
            "template.yaml": "AWS CloudFormation/SAM",
            "cloudformation.yaml": "CloudFormation",
            "ansible.cfg": "Ansible",
            "playbook.yml": "Ansible",
            "Chart.yaml": "Helm",
            "kustomization.yaml": "Kustomize",
            "skaffold.yaml": "Skaffold",
            # Build tools
            "Makefile": "Make",
            "CMakeLists.txt": "CMake",
            "meson.build": "Meson",
            "BUILD": "Bazel",
            "WORKSPACE": "Bazel",
            "webpack.config.js": "Webpack",
            "vite.config.js": "Vite",
            "vite.config.ts": "Vite",
            "rollup.config.js": "Rollup",
            "esbuild.config.js": "esbuild",
            "turbo.json": "Turborepo",
            "nx.json": "Nx",
            "lerna.json": "Lerna",
            # Testing
            "jest.config.js": "Jest",
            "vitest.config.js": "Vitest",
            "cypress.config.js": "Cypress",
            "playwright.config.ts": "Playwright",
            ".mocharc.json": "Mocha",
            "karma.conf.js": "Karma",
            "pytest.ini": "pytest",
            "tox.ini": "tox",
            "phpunit.xml": "PHPUnit",
            # Linting/Formatting
            ".eslintrc.js": "ESLint",
            ".prettierrc": "Prettier",
            "biome.json": "Biome",
            ".rubocop.yml": "RuboCop",
            ".pylintrc": "pylint",
            "mypy.ini": "mypy",
            ".flake8": "flake8",
            "rustfmt.toml": "rustfmt"
        }
        
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if not self.repo_service._should_ignore(d)]
            for item in files + dirs:
                if item in file_tech_map:
                    tech_stack.add(file_tech_map[item])
            # Only check top few levels
            if root.count(os.sep) - source_path.count(os.sep) > 2:
                break
        
        # Check dependencies for frameworks/libraries
        dep_names = [d.get("name", "").lower() for d in dependencies]
        
        framework_map = {
            # Frontend frameworks
            "react": "React", "react-dom": "React",
            "vue": "Vue.js", "@vue/core": "Vue.js",
            "angular": "Angular", "@angular/core": "Angular",
            "svelte": "Svelte", "@sveltejs/kit": "SvelteKit",
            "solid-js": "Solid.js",
            "preact": "Preact",
            "lit": "Lit",
            "alpine": "Alpine.js",
            "htmx": "htmx",
            "stimulus": "Stimulus",
            # Meta frameworks
            "next": "Next.js", "nuxt": "Nuxt.js",
            "gatsby": "Gatsby", "astro": "Astro",
            "remix": "Remix", "@remix-run": "Remix",
            "qwik": "Qwik",
            # Backend frameworks
            "express": "Express.js",
            "fastify": "Fastify",
            "koa": "Koa",
            "hapi": "Hapi",
            "nestjs": "NestJS", "@nestjs/core": "NestJS",
            "fastapi": "FastAPI",
            "flask": "Flask",
            "django": "Django",
            "starlette": "Starlette",
            "aiohttp": "aiohttp",
            "tornado": "Tornado",
            "spring": "Spring Boot",
            "spring-boot": "Spring Boot",
            "quarkus": "Quarkus",
            "micronaut": "Micronaut",
            "rails": "Ruby on Rails",
            "sinatra": "Sinatra",
            "laravel": "Laravel",
            "symfony": "Symfony",
            "codeigniter": "CodeIgniter",
            "gin": "Gin (Go)",
            "echo": "Echo (Go)",
            "fiber": "Fiber (Go)",
            "actix": "Actix Web (Rust)",
            "axum": "Axum (Rust)",
            "rocket": "Rocket (Rust)",
            "phoenix": "Phoenix (Elixir)",
            # Mobile
            "react-native": "React Native",
            "flutter": "Flutter",
            "expo": "Expo",
            "ionic": "Ionic",
            "capacitor": "Capacitor",
            # AI/ML
            "tensorflow": "TensorFlow",
            "pytorch": "PyTorch", "torch": "PyTorch",
            "keras": "Keras",
            "scikit-learn": "Scikit-learn", "sklearn": "Scikit-learn",
            "transformers": "Hugging Face Transformers",
            "langchain": "LangChain",
            "openai": "OpenAI API",
            "anthropic": "Anthropic API",
            "llama-index": "LlamaIndex",
            "pandas": "Pandas",
            "numpy": "NumPy",
            "scipy": "SciPy",
            "matplotlib": "Matplotlib",
            "seaborn": "Seaborn",
            "plotly": "Plotly",
            "streamlit": "Streamlit",
            "gradio": "Gradio",
            # Databases
            "mongoose": "MongoDB",
            "mongodb": "MongoDB",
            "prisma": "Prisma",
            "sequelize": "Sequelize",
            "typeorm": "TypeORM",
            "drizzle": "Drizzle ORM",
            "sqlalchemy": "SQLAlchemy",
            "peewee": "Peewee",
            "diesel": "Diesel (Rust)",
            "sea-orm": "SeaORM (Rust)",
            "gorm": "GORM (Go)",
            "ent": "Ent (Go)",
            "activerecord": "ActiveRecord",
            "eloquent": "Eloquent",
            "redis": "Redis",
            "elasticsearch": "Elasticsearch",
            "neo4j": "Neo4j",
            # API
            "graphql": "GraphQL",
            "apollo": "Apollo GraphQL",
            "@apollo/server": "Apollo Server",
            "trpc": "tRPC",
            "grpc": "gRPC",
            "protobuf": "Protocol Buffers",
            "swagger": "Swagger/OpenAPI",
            "openapi": "OpenAPI",
            # Styling
            "tailwindcss": "Tailwind CSS",
            "bootstrap": "Bootstrap",
            "@mui/material": "Material UI",
            "material-ui": "Material UI",
            "chakra-ui": "Chakra UI",
            "@chakra-ui": "Chakra UI",
            "ant-design": "Ant Design",
            "antd": "Ant Design",
            "styled-components": "Styled Components",
            "@emotion": "Emotion",
            "sass": "Sass",
            "less": "Less",
            # State management
            "redux": "Redux",
            "@reduxjs/toolkit": "Redux Toolkit",
            "zustand": "Zustand",
            "jotai": "Jotai",
            "recoil": "Recoil",
            "mobx": "MobX",
            "pinia": "Pinia",
            "vuex": "Vuex",
            # Testing
            "jest": "Jest",
            "vitest": "Vitest",
            "mocha": "Mocha",
            "cypress": "Cypress",
            "playwright": "Playwright",
            "puppeteer": "Puppeteer",
            "selenium": "Selenium",
            "pytest": "pytest",
            "unittest": "unittest",
            "rspec": "RSpec",
            "junit": "JUnit",
            # Auth
            "passport": "Passport.js",
            "next-auth": "NextAuth.js",
            "auth0": "Auth0",
            "firebase-admin": "Firebase",
            "supabase": "Supabase",
            # Cloud
            "aws-sdk": "AWS SDK",
            "@aws-sdk": "AWS SDK",
            "boto3": "AWS (boto3)",
            "@azure": "Azure SDK",
            "@google-cloud": "Google Cloud SDK",
            "firebase": "Firebase"
        }
        
        for dep in dep_names:
            for key, tech in framework_map.items():
                if key in dep:
                    tech_stack.add(tech)
        
        # Add language from dependencies
        for dep in dependencies:
            lang = dep.get("language")
            if lang:
                tech_stack.add(lang)
        
        return list(tech_stack)
    
    async def _gather_code_context(self, source_path: str, max_files: int = 50) -> str:
        """Gather code context for AI analysis - supports any programming language"""
        context_parts = []
        file_count = 0
        
        # Priority files - comprehensive list for all languages
        priority_files = [
            # Documentation
            "README.md", "readme.md", "README.rst", "README.txt", "README",
            "CONTRIBUTING.md", "CHANGELOG.md", "docs/index.md",
            # JavaScript/TypeScript
            "package.json", "index.js", "index.ts", "app.js", "app.ts",
            "main.js", "main.ts", "src/index.js", "src/index.ts",
            "App.js", "App.jsx", "App.tsx", "server.js", "server.ts",
            # Python
            "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
            "main.py", "app.py", "__main__.py", "manage.py", "wsgi.py", "asgi.py",
            # Java
            "pom.xml", "build.gradle", "build.gradle.kts",
            "Main.java", "Application.java", "App.java",
            # Go
            "go.mod", "main.go", "cmd/main.go",
            # Rust
            "Cargo.toml", "main.rs", "lib.rs", "src/main.rs", "src/lib.rs",
            # Ruby
            "Gemfile", "Rakefile", "config.ru", "app.rb", "application.rb",
            "config/application.rb", "config/routes.rb",
            # PHP
            "composer.json", "index.php", "artisan",
            "app/Http/Kernel.php", "routes/web.php",
            # C/C++
            "CMakeLists.txt", "Makefile", "main.c", "main.cpp", "main.h",
            # C#/.NET
            "Program.cs", "Startup.cs", "appsettings.json",
            # Swift
            "Package.swift", "main.swift", "App.swift", "ContentView.swift",
            # Kotlin
            "build.gradle.kts", "Main.kt", "Application.kt",
            # Dart/Flutter
            "pubspec.yaml", "main.dart", "lib/main.dart",
            # Elixir
            "mix.exs", "lib/application.ex", "config/config.exs",
            # Haskell
            "stack.yaml", "Main.hs", "app/Main.hs",
            # Julia
            "Project.toml", "src/main.jl",
            # R
            "DESCRIPTION", "R/main.R",
            # Scala
            "build.sbt", "Main.scala",
            # Clojure
            "project.clj", "deps.edn", "src/core.clj",
            # Config/DevOps
            "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
            ".env.example", "config.yaml", "config.json",
            "terraform.tf", "main.tf", "serverless.yml"
        ]
        
        # First, add priority files
        for priority_file in priority_files:
            for root, dirs, files in os.walk(source_path):
                dirs[:] = [d for d in dirs if not self.repo_service._should_ignore(d)]
                if priority_file in files:
                    file_path = os.path.join(root, priority_file)
                    relative_path = os.path.relpath(file_path, source_path)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()[:5000]  # Limit content size
                        context_parts.append(f"=== {relative_path} ===\n{content}\n")
                        file_count += 1
                    except:
                        pass
                    break
            if file_count >= max_files:
                break
        
        # Then add other important files
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if not self.repo_service._should_ignore(d)]
            
            for filename in files:
                if file_count >= max_files:
                    break
                
                if self.repo_service._should_ignore(filename):
                    continue
                
                _, ext = os.path.splitext(filename)
                if ext not in settings.SUPPORTED_EXTENSIONS:
                    continue
                
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, source_path)
                
                # Skip if already added
                if any(relative_path in part for part in context_parts):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()[:3000]  # Limit content size
                    context_parts.append(f"=== {relative_path} ===\n{content}\n")
                    file_count += 1
                except:
                    pass
            
            if file_count >= max_files:
                break
        
        return "\n".join(context_parts)
