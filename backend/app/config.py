"""
Application Configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # API Settings
    APP_NAME: str = "Repository Analyzer"
    DEBUG: bool = True
    
    # AI Provider Settings: "openai", "ollama", "gemini"
    AI_PROVIDER: str = "gemini"
    
    # OpenAI Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Ollama Settings (free, local)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    
    # Google Gemini Settings (free tier available)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # Storage Settings
    UPLOAD_DIR: str = "./uploads"
    CLONE_DIR: str = "./cloned_repos"
    REPORTS_DIR: str = "./reports"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"]
    
    # Analysis Settings
    MAX_FILE_SIZE_MB: int = 100
    SUPPORTED_EXTENSIONS: List[str] = [
        # Python
        ".py", ".pyw", ".pyx", ".pxd", ".pxi", ".ipynb",
        # JavaScript/TypeScript
        ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts",
        # Java/JVM Languages
        ".java", ".kt", ".kts", ".scala", ".sc", ".groovy", ".gradle", ".clj", ".cljs",
        # C/C++/Objective-C
        ".c", ".h", ".cpp", ".hpp", ".cc", ".hh", ".cxx", ".hxx", ".c++", ".h++", ".m", ".mm",
        # C#/F#/.NET
        ".cs", ".csx", ".fs", ".fsx", ".vb", ".xaml",
        # Go
        ".go", ".mod", ".sum",
        # Rust
        ".rs", ".rlib",
        # Ruby
        ".rb", ".erb", ".rake", ".gemspec", ".ru",
        # PHP
        ".php", ".phtml", ".php3", ".php4", ".php5", ".php7", ".phps",
        # Swift/Objective-C
        ".swift", ".playground",
        # Perl
        ".pl", ".pm", ".pod", ".t",
        # Lua
        ".lua",
        # R
        ".r", ".R", ".rmd", ".Rmd",
        # Julia
        ".jl",
        # Haskell
        ".hs", ".lhs", ".cabal",
        # Elixir/Erlang
        ".ex", ".exs", ".erl", ".hrl",
        # Dart/Flutter
        ".dart",
        # COBOL
        ".cob", ".cbl", ".cobol",
        # Fortran
        ".f", ".for", ".f90", ".f95", ".f03", ".f08",
        # Assembly
        ".asm", ".s", ".S",
        # Shell/Scripting
        ".sh", ".bash", ".zsh", ".fish", ".ps1", ".psm1", ".psd1", ".bat", ".cmd",
        # Web/Markup
        ".html", ".htm", ".xhtml", ".css", ".scss", ".sass", ".less", ".styl",
        ".vue", ".svelte", ".astro", ".ejs", ".hbs", ".handlebars", ".pug", ".jade",
        # Data/Config
        ".json", ".json5", ".jsonc", ".yaml", ".yml", ".toml", ".xml", ".xsl", ".xslt",
        ".ini", ".cfg", ".conf", ".config", ".env", ".properties",
        # Database
        ".sql", ".pgsql", ".mysql", ".plsql", ".ddl", ".dml",
        # Documentation
        ".md", ".markdown", ".rst", ".txt", ".adoc", ".asciidoc", ".tex", ".org",
        # DevOps/IaC
        ".dockerfile", ".tf", ".tfvars", ".hcl", ".nomad", ".sentinel",
        ".ansible", ".jenkinsfile", ".Makefile", ".makefile", ".mk", ".cmake",
        # GraphQL/API
        ".graphql", ".gql", ".proto", ".thrift", ".avsc",
        # Solidity/Blockchain
        ".sol", ".vy",
        # Other Languages
        ".nim", ".zig", ".v", ".d", ".cr", ".ml", ".mli", ".ocaml",
        ".elm", ".purs", ".rkt", ".scm", ".lisp", ".cl",
        ".tcl", ".awk", ".sed", ".vhd", ".vhdl", ".sv", ".svh",
        # Misc
        ".gitignore", ".dockerignore", ".editorconfig"
    ]
    
    # File patterns to ignore
    IGNORE_PATTERNS: List[str] = [
        "node_modules", "__pycache__", ".git", ".svn", "venv", "env",
        ".idea", ".vscode", "dist", "build", ".next", "target",
        "*.pyc", "*.pyo", "*.exe", "*.dll", "*.so", "*.dylib",
        "package-lock.json", "yarn.lock", "poetry.lock"
    ]


settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CLONE_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
