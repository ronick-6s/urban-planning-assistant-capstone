import os
import certifi
from dotenv import load_dotenv

load_dotenv()

# Verbose output control - completely disable for clean chatbot experience
VERBOSE_OUTPUT = False
SILENT_MODE = True

# Set SSL certificates
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()

# LangSmith
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

# MongoDB Atlas (Legacy - keeping for compatibility)
MONGO_ATLAS_URI = os.getenv("MONGO_ATLAS_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "urban_planning_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", os.getenv("USER", "ronick"))
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# Neo4j Aura
NEO4J_AURA_URI = os.getenv("NEO4J_AURA_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Model
MODEL_NAME = "gemini-flash-latest"

# Embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
