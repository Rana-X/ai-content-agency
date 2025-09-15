"""
Configuration module for AI Content Agency
Handles environment variables and application settings
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class Config:
    """Application configuration class"""
    
    # Gemini API Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY: str = os.getenv('SUPABASE_KEY', '')
    
    # LangSmith Configuration
    LANGCHAIN_TRACING_V2: bool = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
    LANGCHAIN_ENDPOINT: str = os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
    LANGCHAIN_API_KEY: str = os.getenv('LANGCHAIN_API_KEY', '')
    LANGCHAIN_PROJECT: str = os.getenv('LANGCHAIN_PROJECT', 'ai-content-agency')
    
    # Application Settings
    APP_ENV: str = os.getenv('APP_ENV', 'development')
    APP_PORT: int = int(os.getenv('APP_PORT', '8000'))
    APP_HOST: str = os.getenv('APP_HOST', '0.0.0.0')
    
    # Workflow Settings
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '2'))
    DEFAULT_WORKFLOW_MODE: str = os.getenv('DEFAULT_WORKFLOW_MODE', 'standard')
    QUALITY_THRESHOLD: float = float(os.getenv('QUALITY_THRESHOLD', '60'))
    
    # Rate Limiting
    GEMINI_REQUESTS_PER_MINUTE: int = int(os.getenv('GEMINI_REQUESTS_PER_MINUTE', '60'))
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    
    # Directory Paths
    BASE_DIR: Path = Path(__file__).parent
    AGENTS_DIR: Path = BASE_DIR / 'agents'
    WORKFLOWS_DIR: Path = BASE_DIR / 'workflows'
    STATE_DIR: Path = BASE_DIR / 'state'
    API_DIR: Path = BASE_DIR / 'api'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_vars = {
            'GEMINI_API_KEY': cls.GEMINI_API_KEY,
            'SUPABASE_URL': cls.SUPABASE_URL,
            'SUPABASE_KEY': cls.SUPABASE_KEY
        }
        
        missing = []
        for var_name, var_value in required_vars.items():
            if not var_value or var_value == f'your_{var_name.lower()}_here':
                missing.append(var_name)
        
        if missing:
            logger.error(f"Missing required configuration: {', '.join(missing)}")
            logger.info("Please update your .env file with valid values")
            return False
        
        # Optional: Validate LangSmith if enabled
        if cls.LANGCHAIN_TRACING_V2 and not cls.LANGCHAIN_API_KEY:
            logger.warning("LangSmith tracing enabled but API key not provided")
        
        logger.info("Configuration validated successfully")
        return True
    
    @classmethod
    def get_supabase_client(cls):
        """Get Supabase client instance"""
        from supabase import create_client, Client
        
        if not cls.SUPABASE_URL or not cls.SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured")
        
        return create_client(cls.SUPABASE_URL, cls.SUPABASE_KEY)
    
    @classmethod
    def get_gemini_client(cls):
        """Get Gemini client instance"""
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        if not cls.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
        
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=cls.GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=2048
        )
    
    @classmethod
    def setup_langsmith(cls):
        """Setup LangSmith tracing if enabled"""
        if cls.LANGCHAIN_TRACING_V2:
            os.environ['LANGCHAIN_TRACING_V2'] = 'true'
            os.environ['LANGCHAIN_ENDPOINT'] = cls.LANGCHAIN_ENDPOINT
            os.environ['LANGCHAIN_API_KEY'] = cls.LANGCHAIN_API_KEY
            os.environ['LANGCHAIN_PROJECT'] = cls.LANGCHAIN_PROJECT
            logger.info(f"LangSmith tracing enabled for project: {cls.LANGCHAIN_PROJECT}")
        else:
            logger.info("LangSmith tracing disabled")

# Constants
MAX_CHECKPOINT_HISTORY = 10
DEFAULT_WORD_COUNT_TARGET = 1000
MIN_SOURCES_REQUIRED = 3

# Workflow States
class WorkflowStatus:
    CREATED = "created"
    STARTED = "started"
    RESEARCHING = "researching"
    WRITING = "writing"
    REVIEWING = "reviewing"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    REVISING = "revising"
    COMPLETED = "completed"
    FAILED = "failed"

# Agent Names
class AgentNames:
    MANAGER = "manager"
    RESEARCH = "research"
    WRITER = "writer"
    REVIEW = "review"

# Initialize configuration
config = Config()

# Setup LangSmith if configured
if config.APP_ENV != 'test':
    config.setup_langsmith()

logger.info(f"Application started in {config.APP_ENV} mode")