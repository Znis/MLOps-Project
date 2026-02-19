from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ALLOW_ORIGINS: str = '*'
    # LLM: Ollama (local)
    OLLAMA_HOST: str = 'http://localhost:11434'
    OLLAMA_MODEL: str = 'Qwen-0.6B'
    # Embeddings (sentence-transformers, local)
    EMBEDDING_MODEL: str = 'BAAI/bge-small-en-v1.5'
    EMBEDDING_DIMENSIONS: int = 384  # bge-small-en-v1.5 output dimension
    # Vector DB: Qdrant
    QDRANT_URL: str = 'http://98.92.135.201:6334'
    QDRANT_GRPC: bool = True
    QDRANT_COLLECTION: str = 'documents'
    # Chat history: Redis
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    EXPORT_DIR: str = 'data'
    VECTOR_SEARCH_TOP_K: int = 10
    # Indexing: fixed-size chunking (chars)
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    model_config = SettingsConfigDict(env_file='.env')

settings = Settings()