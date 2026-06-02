"""
配置文件：集中管理 DeepSeek API Key、Milvus 地址、模型参数
"""
import os
from dotenv import load_dotenv

load_dotenv()

# DeepSeek API
DEEPSEEK_API_KEY = "sk-7efa3d35e96e44fe9b80b135b6b764b1"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Milvus
MILVUS_HOST = "localhost"
MILVUS_PORT = 19530
MILVUS_DB_NAME = "default"

# Collection names
FILE_CHUNKS_COLLECTION = "file_chunks"
QA_PAIRS_COLLECTION = "qa_pairs"

# Embedding
EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh-v1.5"
EMBEDDING_DIM = 768

# Retrieval defaults
DEFAULT_TOP_K = 5
