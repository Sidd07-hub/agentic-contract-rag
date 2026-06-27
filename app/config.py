"""
Application configuration.

Loads environment variables and defines project-wide settings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Project Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

CONTRACTS_DIR = DATA_DIR / "contracts"
SCHEMA_DIR = DATA_DIR / "schema"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
OUTPUT_DIR = DATA_DIR / "output"

# --------------------------------------------------
# LLM Configuration
# --------------------------------------------------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# --------------------------------------------------
# Embedding Model
# --------------------------------------------------
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5",
)

# --------------------------------------------------
# Retrieval
# --------------------------------------------------
TOP_K_RESULTS = int(
    os.getenv("TOP_K_RESULTS", "3")
)

# --------------------------------------------------
# Chunking
# --------------------------------------------------
CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", "1000")
)

CHUNK_OVERLAP = int(
    os.getenv("CHUNK_OVERLAP", "200")
)

# --------------------------------------------------
# Logging
# --------------------------------------------------
LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
)