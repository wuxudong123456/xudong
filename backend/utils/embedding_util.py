"""
Embedding 向量化工具
使用本地 BAAI/bge-small-zh-v1.5 模型将文本转为向量
免费、离线、中文优化，512维
支持 HuggingFace 镜像源，适配国内网络环境
"""
import os
import logging
from typing import List

logger = logging.getLogger("embedding")

MODEL_NAME = "BAAI/bge-small-zh-v1.5"
VECTOR_DIM = 512

# 全局单例模型（懒加载）
_model = None
_model_error = None


def _get_model():
    global _model, _model_error

    if _model is not None:
        return _model

    # 如果之前加载失败了，直接抛出
    if _model_error is not None:
        raise _model_error

    try:
        from sentence_transformers import SentenceTransformer

        # 支持通过环境变量 / .env 配置 HuggingFace 镜像
        mirror = os.environ.get("HF_MIRROR", os.environ.get("HF_ENDPOINT", ""))
        if not mirror:
            try:
                from backend.config import settings
                mirror = settings.HF_ENDPOINT
            except Exception:
                pass
        if mirror:
            logger.info("使用 HuggingFace 镜像: %s", mirror)
            os.environ.setdefault("HF_ENDPOINT", mirror)

        _model = SentenceTransformer(MODEL_NAME)
        logger.info("Embedding 模型加载成功: %s (维度=%d)", MODEL_NAME, VECTOR_DIM)
        return _model

    except Exception as e:
        error_msg = str(e)
        if "Connection" in error_msg or "timed out" in error_msg or "Network" in error_msg:
            hint = (
                "无法从 HuggingFace 下载模型文件（约300MB）。国内网络环境下请设置镜像：\n"
                "  方案1: 设置环境变量 HF_ENDPOINT=https://hf-mirror.com\n"
                "  方案2: 手动下载模型到本地，设置 HF_HOME 指向模型目录\n"
                "  方案3: 使用代理 export HTTP_PROXY=http://your-proxy:port"
            )
            logger.error("Embedding 模型下载失败（网络问题）:\n%s", hint)
            _model_error = RuntimeError(f"模型下载失败：{error_msg}\n{hint}")
        else:
            logger.error("Embedding 模型加载失败: %s", e)
            _model_error = RuntimeError(f"模型加载失败：{error_msg}")
        raise _model_error


async def get_embedding(text: str) -> List[float]:
    """单条文本转向量"""
    import asyncio
    model = _get_model()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: model.encode(text, normalize_embeddings=True).tolist()
    )


async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """批量文本转向量"""
    import asyncio
    model = _get_model()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: model.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()
    )