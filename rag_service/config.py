"""
Configuration module for PharmaRAG service.
Handles environment variables and application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

# Database configuration
CHROMA_PATH = "chroma"
TEMPERATURE = 0.2

# Cache configuration - Optimized for performance
CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL_MINUTES", "30"))  # Increased from 10 to 30 minutes
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "2000"))  # Increased from 1000 to 2000
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"

# Memory cache configuration
MEMORY_CACHE_SIZE = int(os.getenv("MEMORY_CACHE_SIZE", "100"))  # Number of documents to keep in memory
MEMORY_CACHE_TTL_HOURS = int(os.getenv("MEMORY_CACHE_TTL_HOURS", "2"))  # Memory cache TTL

# Database optimization settings
DB_CONNECTION_POOL_SIZE = int(os.getenv("DB_CONNECTION_POOL_SIZE", "5"))
DB_QUERY_TIMEOUT_MS = int(os.getenv("DB_QUERY_TIMEOUT_MS", "5000"))
DB_MAX_RESULTS = int(os.getenv("DB_MAX_RESULTS", "100"))

# API configuration
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# Log API key status (without exposing the actual key)
if API_KEY:
    logger.info("API_KEY loaded successfully")
else:
    logger.warning("API_KEY not found in environment variables")

# Service configuration
SERVICE_NAME = "PharmaRAG Service"
SERVICE_VERSION = "1.0.0"
SERVICE_HOST = "0.0.0.0"
SERVICE_PORT = 8000

# Performance monitoring
ENABLE_PERFORMANCE_MONITORING = os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true"
PERFORMANCE_LOG_THRESHOLD_MS = int(os.getenv("PERFORMANCE_LOG_THRESHOLD_MS", "1000"))  # Log operations taking longer than this
