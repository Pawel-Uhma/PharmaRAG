"""
Main entry point for PharmaRAG service.
Simplified and restructured into modular components.
"""

import os
import logging
import uvicorn

try:
    from .config import API_KEY, CHROMA_PATH, SERVICE_HOST, SERVICE_PORT
    from .api import create_app
except ImportError:
    # Handle direct execution
    from config import API_KEY, CHROMA_PATH, SERVICE_HOST, SERVICE_PORT
    from api import create_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = create_app()


def main():
    """Main function to start the PharmaRAG service."""
    try:
        logger.info("Starting PharmaRAG Service...")
        logger.info(f"Chroma path: {CHROMA_PATH}")
        
        # Validate environment
        if not API_KEY:
            logger.error("API_KEY not found! Please check your .env file.")
            exit(1)
        
        # Check if Chroma directory exists
        if not os.path.exists(CHROMA_PATH):
            logger.warning(f"Chroma directory {CHROMA_PATH} does not exist. It will be created on first use.")
        
        logger.info(f"Service will be available at http://{SERVICE_HOST}:{SERVICE_PORT}")
        logger.info("CORS is enabled for localhost:3000")
        uvicorn.run(app, host=SERVICE_HOST, port=SERVICE_PORT)
    except Exception as e:
        logger.error(f"Failed to start service: {str(e)}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()
