import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BASE_DIR = Path(__file__).parent.parent

DATA_RAW = BASE_DIR / 'data' / 'dataset'
VECTORSTORE_DIR = BASE_DIR / 'App' / 'backend' / 'vectorstore'

EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# Cloud LLM
LLM_BACKEND = os.getenv('LLM_BACKEND', 'cloud')
LLM_API_BASE = os.getenv('LLM_API_BASE', 'https://api.groq.com/openai/v1')
LLM_API_KEY = os.getenv('LLM_API_KEY', '')
LLM_API_MODEL = os.getenv('LLM_API_MODEL', 'llama-3.1-8b-instant')

OUTPUT_DIR = BASE_DIR / 'output'

CHROMA_COLLECTION_NAME = 'prd_docs'
RAG_TOP_K_DISKUSI = 2
RAG_TOP_K_EKSEKUSI = 3
MAX_INPUT_TOKENS = 3072
MAX_OUTPUT_TOKENS = 768
