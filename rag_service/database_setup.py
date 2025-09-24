"""
Database setup script for PharmaRAG PostgreSQL with pgvector extension.
This script helps set up the PostgreSQL database with the required extensions.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
import logging
from dotenv import load_dotenv

# Load environment variables from config.env file
load_dotenv('.env')

logger = logging.getLogger(__name__)

# Database configuration from environment variables
POSTGRES_CONNECTION_STRING = os.getenv('DATABASE_URL')
DB_NAME = os.getenv('DB_NAME', 'pharmarag')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Validate required environment variables
        if not all([DB_HOST, DB_USER, DB_PASSWORD]):
            raise ValueError("Missing required database environment variables: DB_HOST, DB_USER, DB_PASSWORD")
        
        # Connect to postgres database to create our database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            logger.info(f"Database '{DB_NAME}' created successfully")
        else:
            logger.info(f"Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return False

def setup_extensions():
    """Set up required PostgreSQL extensions (pgvector)."""
    try:
        if not POSTGRES_CONNECTION_STRING:
            raise ValueError("Missing required DATABASE_URL environment variable")
        
        engine = create_engine(POSTGRES_CONNECTION_STRING)
        
        with engine.connect() as conn:
            # Enable pgvector extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("pgvector extension enabled successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up extensions: {str(e)}")
        return False

def test_connection():
    """Test the database connection."""
    try:
        if not POSTGRES_CONNECTION_STRING:
            raise ValueError("Missing required DATABASE_URL environment variable")
        
        engine = create_engine(POSTGRES_CONNECTION_STRING)
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            
            # Test pgvector extension
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"PostgreSQL version: {version}")
            
            # Test vector extension
            result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
            if result.fetchone():
                logger.info("pgvector extension is available")
            else:
                logger.warning("pgvector extension not found")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        return False

def main():
    """Main setup function."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Setting up PharmaRAG PostgreSQL database...")
    
    # Step 1: Create database
    if not create_database():
        logger.error("Failed to create database")
        return False
    
    # Step 2: Setup extensions
    if not setup_extensions():
        logger.error("Failed to setup extensions")
        return False
    
    # Step 3: Test connection
    if not test_connection():
        logger.error("Failed to test connection")
        return False
    
    logger.info("Database setup completed successfully!")
    logger.info("You can now run the ingestion script to populate the database.")
    
    return True

if __name__ == "__main__":
    main()


