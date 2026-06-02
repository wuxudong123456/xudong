"""
嵌入模型封装：使用 BAAI/bge-small-zh-v1.5（768 维）
"""
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL_NAME, EMBEDDING_DIM

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"正在加载嵌入模型: {EMBEDDING_MODEL_NAME} ...")
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        dim = _model.get_embedding_dimension()
        print(f"嵌入模型加载完成，向量维度: {dim}")
    return _model


def get_dim() -> int:
    return get_model().get_embedding_dimension()


def encode(text: str) -> list[float]:
    """将单条文本编码为向量"""
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def encode_batch(texts: list[str]) -> list[list[float]]:
    """批量编码"""
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return embeddings.tolist()
