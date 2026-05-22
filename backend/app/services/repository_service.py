"""
Repository Service - Handles repository operations
"""

import os
import shutil
import zipfile
import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from app.config import settings
import json
import fnmatch

# Fix for Windows asyncio subprocess
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class RepositoryService:
    """Service for handling repository operations"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.clone_dir = settings.CLONE_DIR
        self.metadata_file = "repo_metadata.json"
    
    def _normalize_git_url(self, url: str) -> tuple[str, str]:
        """
        Normalize a Git URL to handle both SSH and HTTPS formats.
        Returns (normalized_url, repo_name)
        
        Supports:
        - HTTPS: https://github.com/user/repo.git
        - HTTPS without .git: https://github.com/user/repo
        - SSH: git@github.com:user/repo.git
        - SSH without .git: git@github.com:user/repo
        """
        url = url.strip()
        repo_name = ""
        
        # Handle SSH format: git@github.com:user/repo.git
        if url.startswith('git@'):
            # Extract repo name from SSH URL
            # git@github.com:user/repo.git -> user/repo.git
            if ':' in url:
                path_part = url.split(':')[-1]
                repo_name = path_part.rstrip('/').split('/')[-1].replace('.git', '')
        
        # Handle HTTPS format: https://github.com/user/repo.git
        elif url.startswith('http://') or url.startswith('https://'):
            repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
        
        # Handle other formats (just extract last part)
        else:
            repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
        
        return url, repo_name
    
    def _is_valid_git_url(self, url: str) -> bool:
        """
        Validate if a URL is a valid Git repository URL.
        Supports both SSH and HTTPS formats.
        """
        url = url.strip()
        
        # HTTPS patterns
        https_patterns = [
            # Standard HTTPS with .git
            url.startswith('https://') and '.git' in url,
            # GitHub HTTPS without .git
            url.startswith('https://github.com/') and '/' in url[19:],
            # GitLab HTTPS without .git
            url.startswith('https://gitlab.com/') and '/' in url[19:],
            # Bitbucket HTTPS without .git
            url.startswith('https://bitbucket.org/') and '/' in url[22:],
            # Generic HTTPS Git URL
            url.startswith('http://') or url.startswith('https://'),
        ]
        
        # SSH patterns
        ssh_patterns = [
            # Standard SSH: git@github.com:user/repo.git
            url.startswith('git@') and ':' in url,
            # SSH with ssh:// prefix
            url.startswith('ssh://git@'),
        ]
        
        return any(https_patterns) or any(ssh_patterns)
    
    async def process_uploaded_zip(self, file, repo_id: str) -> Dict[str, Any]:
        """Process an uploaded ZIP file"""
        # Create repository directory
        repo_path = os.path.join(self.upload_dir, repo_id)
        os.makedirs(repo_path, exist_ok=True)
        
        # Save the ZIP file
        zip_path = os.path.join(repo_path, "repository.zip")
        content = await file.read()
        with open(zip_path, "wb") as f:
            f.write(content)
        
        # Extract the ZIP file
        extract_path = os.path.join(repo_path, "source")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Security: Check for path traversal in ZIP entries
            for member in zip_ref.namelist():
                member_path = os.path.realpath(os.path.join(extract_path, member))
                if not member_path.startswith(os.path.realpath(extract_path)):
                    raise Exception("ZIP file contains unsafe path traversal entries")
            zip_ref.extractall(extract_path)
        
        # Get repository name from ZIP or folder
        extracted_items = os.listdir(extract_path)
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(extract_path, extracted_items[0])):
            repo_name = extracted_items[0]
            source_path = os.path.join(extract_path, repo_name)
        else:
            repo_name = file.filename.replace('.zip', '')
            source_path = extract_path
        
        # Count files
        file_count = self._count_files(source_path)
        
        # Save metadata
        metadata = {
            "id": repo_id,
            "name": repo_name,
            "source": "zip_upload",
            "path": source_path,
            "file_count": file_count,
            "original_filename": file.filename
        }
        self._save_metadata(repo_path, metadata)
        
        return {"name": repo_name, "file_count": file_count, "path": source_path}
    
    async def clone_repository(self, url: str, repo_id: str, branch: str = "main") -> Dict[str, Any]:
        """
        Clone a Git repository (async, non-blocking).

        Supports both SSH and HTTPS URLs:
        - HTTPS: https://github.com/user/repo.git
        - SSH: git@github.com:user/repo.git
        """
        # Normalize and validate the URL
        normalized_url, repo_name = self._normalize_git_url(url)

        if not self._is_valid_git_url(normalized_url):
            raise Exception(
                "Invalid Git URL format. Supported formats:\n"
                "- HTTPS: https://github.com/username/repository.git\n"
                "- SSH: git@github.com:username/repository.git"
            )

        # Create repository directory
        repo_path = os.path.join(self.clone_dir, repo_id)
        os.makedirs(repo_path, exist_ok=True)

        source_path = os.path.join(repo_path, "source")

        # Disable ALL credential prompts so git never hangs waiting for user input
        git_env = os.environ.copy()
        git_env["GIT_TERMINAL_PROMPT"] = "0"
        git_env["GIT_ASKPASS"] = "echo"
        git_env["GCM_INTERACTIVE"] = "never"
        git_env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes -o StrictHostKeyChecking=no"

        def _parse_error(stderr: str) -> str:
            if "Authentication failed" in stderr or "could not read Username" in stderr or "Access denied" in stderr:
                return (
                    "Authentication failed. For private repos, use a Personal Access Token:\n"
                    "  https://<token>@github.com/user/repo.git"
                )
            if "Permission denied" in stderr or "publickey" in stderr:
                return "SSH authentication failed. Use an HTTPS URL or set up SSH keys."
            if "not found" in stderr.lower() or "does not exist" in stderr.lower() or "Repository not found" in stderr:
                return f"Repository not found. Check the URL is correct and the repo is public.\n{stderr.strip()}"
            return f"Failed to clone repository: {stderr.strip()}"

        def _run_git(cmd: list) -> tuple:
            """
            Run a git command in a thread (non-blocking on the event loop).
            Returns (returncode, stderr).
            """
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env=git_env,
                )
                return result.returncode, result.stderr
            except subprocess.TimeoutExpired:
                return -1, "timeout"
            except FileNotFoundError:
                return -2, "git_not_found"

        loop = asyncio.get_event_loop()

        try:
            # Attempt 1: shallow clone with specified branch (runs in thread pool)
            returncode, stderr = await loop.run_in_executor(
                None, _run_git,
                ["git", "clone", "--depth", "1", "--branch", branch,
                 "--single-branch", normalized_url, source_path]
            )

            if returncode != 0:
                if os.path.exists(source_path):
                    shutil.rmtree(source_path)

                if stderr == "timeout":
                    raise Exception("Clone timed out (2 min). The repo may be too large or unreachable.")
                if stderr == "git_not_found":
                    raise Exception("Git is not installed or not in PATH. Please install Git first.")

                # Attempt 2: shallow clone without branch spec (uses default branch)
                returncode, stderr = await loop.run_in_executor(
                    None, _run_git,
                    ["git", "clone", "--depth", "1", normalized_url, source_path]
                )

                if returncode != 0:
                    if os.path.exists(source_path):
                        shutil.rmtree(source_path)
                    if stderr == "timeout":
                        raise Exception("Clone timed out (2 min). The repo may be too large or unreachable.")
                    if stderr == "git_not_found":
                        raise Exception("Git is not installed or not in PATH. Please install Git first.")
                    raise Exception(_parse_error(stderr))

        except Exception:
            raise
        
        # Count files
        file_count = self._count_files(source_path)
        
        # Save metadata
        metadata = {
            "id": repo_id,
            "name": repo_name,
            "source": "git_clone",
            "path": source_path,
            "file_count": file_count,
            "url": url,
            "branch": branch
        }
        self._save_metadata(repo_path, metadata)
        
        return {"name": repo_name, "file_count": file_count, "path": source_path}
    
    async def get_repository_structure(self, repo_id: str) -> Dict[str, Any]:
        """Get the file structure of a repository"""
        repo_path = self._get_repo_path(repo_id)
        if not repo_path:
            raise FileNotFoundError("Repository not found")
        
        metadata = self._load_metadata(repo_path)
        source_path = metadata.get("path", os.path.join(repo_path, "source"))
        
        structure = self._build_structure(source_path)
        return {
            "name": metadata.get("name"),
            "structure": structure,
            "total_files": self._count_files(source_path),
            "languages": self._detect_languages(source_path)
        }
    
    async def get_file_content(self, repo_id: str, file_path: str) -> str:
        """Get the content of a specific file"""
        repo_path = self._get_repo_path(repo_id)
        if not repo_path:
            raise FileNotFoundError("Repository not found")
        
        metadata = self._load_metadata(repo_path)
        source_path = metadata.get("path", os.path.join(repo_path, "source"))
        
        full_path = os.path.join(source_path, file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError("File not found")
        
        # Security check - ensure file is within repository
        if not os.path.abspath(full_path).startswith(os.path.abspath(source_path)):
            raise PermissionError("Access denied")
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")
    
    async def delete_repository(self, repo_id: str):
        """Delete a repository"""
        repo_path = self._get_repo_path(repo_id)
        if not repo_path:
            raise FileNotFoundError("Repository not found")
        
        shutil.rmtree(repo_path)
    
    async def list_repositories(self) -> List[Dict[str, Any]]:
        """List all repositories"""
        repos = []
        
        # Check upload directory
        if os.path.exists(self.upload_dir):
            for repo_id in os.listdir(self.upload_dir):
                repo_path = os.path.join(self.upload_dir, repo_id)
                if os.path.isdir(repo_path):
                    metadata = self._load_metadata(repo_path)
                    if metadata:
                        repos.append(metadata)
        
        # Check clone directory
        if os.path.exists(self.clone_dir):
            for repo_id in os.listdir(self.clone_dir):
                repo_path = os.path.join(self.clone_dir, repo_id)
                if os.path.isdir(repo_path):
                    metadata = self._load_metadata(repo_path)
                    if metadata:
                        repos.append(metadata)
        
        return repos
    
    def _get_repo_path(self, repo_id: str) -> Optional[str]:
        """Get the path to a repository"""
        # Check upload directory
        upload_path = os.path.join(self.upload_dir, repo_id)
        if os.path.exists(upload_path):
            return upload_path
        
        # Check clone directory
        clone_path = os.path.join(self.clone_dir, repo_id)
        if os.path.exists(clone_path):
            return clone_path
        
        return None
    
    def _save_metadata(self, repo_path: str, metadata: Dict[str, Any]):
        """Save repository metadata"""
        metadata_path = os.path.join(repo_path, self.metadata_file)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_metadata(self, repo_path: str) -> Dict[str, Any]:
        """Load repository metadata"""
        metadata_path = os.path.join(repo_path, self.metadata_file)
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _count_files(self, path: str) -> int:
        """Count the number of files in a directory"""
        count = 0
        for root, dirs, files in os.walk(path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            for file in files:
                if not self._should_ignore(file):
                    count += 1
        return count
    
    def _should_ignore(self, name: str) -> bool:
        """Check if a file/directory should be ignored"""
        for pattern in settings.IGNORE_PATTERNS:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False
    
    def _build_structure(self, path: str, prefix: str = "") -> List[Dict[str, Any]]:
        """Build the directory structure"""
        structure = []
        
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return structure
        
        for item in items:
            if self._should_ignore(item):
                continue
            
            item_path = os.path.join(path, item)
            relative_path = os.path.join(prefix, item) if prefix else item
            
            if os.path.isdir(item_path):
                structure.append({
                    "name": item,
                    "type": "directory",
                    "path": relative_path,
                    "children": self._build_structure(item_path, relative_path)
                })
            else:
                _, ext = os.path.splitext(item)
                structure.append({
                    "name": item,
                    "type": "file",
                    "path": relative_path,
                    "extension": ext,
                    "size": os.path.getsize(item_path)
                })
        
        return structure
    
    def _detect_languages(self, path: str) -> Dict[str, int]:
        """Detect programming languages used in the repository"""
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React JSX",
            ".tsx": "React TSX",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".h": "C/C++ Header",
            ".cs": "C#",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".sass": "Sass",
            ".less": "Less",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".xml": "XML",
            ".md": "Markdown",
            ".sql": "SQL",
            ".sh": "Shell",
            ".bash": "Bash",
            ".ps1": "PowerShell"
        }
        
        languages = {}
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            for file in files:
                if self._should_ignore(file):
                    continue
                _, ext = os.path.splitext(file)
                if ext in language_map:
                    lang = language_map[ext]
                    languages[lang] = languages.get(lang, 0) + 1
        
        return languages
