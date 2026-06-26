import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ----------------------------
# Project Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
CONTRACTS_DIR = DATA_DIR / "contracts"
SCHEMA_DIR = DATA_DIR / "schema"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
OUTPUT_DIR = DATA_DIR / "output"

# ----------------------------
# LLM Configuration
# ----------------------------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.1:8b")

# ----------------------------
# Embedding Model
# ----------------------------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ----------------------------
# Retrieval Configuration
# ----------------------------
TOP_K_RESULTS = 5

# ----------------------------
# Chunking Configuration
# ----------------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ----------------------------
# Logging
# ----------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")