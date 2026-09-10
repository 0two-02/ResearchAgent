"""
ResearchPilot AI - Backend Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# IBM watsonx.ai
IBM_API_KEY = os.getenv("IBM_API_KEY", "")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID", "")
IBM_URL = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")

# Groq (used as LLM fallback when IBM credentials are absent)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
GROQ_AVAILABLE = bool(os.getenv("GROQ_API_KEY", ""))

# Langflow
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "")
LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL", "http://localhost:7860")

# Academic APIs
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./researchpilot.db")

# Vector DB
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

# App
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

# Demo Mode
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Embedding
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Rate limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# Upload directory
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# IBM Model settings
IBM_MODEL_ID = "ibm/granite-13b-chat-v2"
IBM_MODEL_PARAMS = {
    "max_new_tokens": 2048,
    "min_new_tokens": 10,
    "temperature": 0.3,
    "top_p": 0.9,
    "repetition_penalty": 1.1,
}

# Check if IBM credentials are available
IBM_AVAILABLE = bool(IBM_API_KEY and IBM_PROJECT_ID)
