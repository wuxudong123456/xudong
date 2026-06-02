"""
统一LLM路由层
自动选择DeepSeek或阿里云，支持故障转移
"""
import logging
from typing import List, Dict, Optional, AsyncGenerator
from backend.config import settings
from backend.utils import deepseek_util, qwen_util

logger = logging.getLogger("llm_router")

# 模型能力映射
MODEL_CAPABILITIES = {
    "deepseek": ["chat", "stream", "function_calling"],
    "aliyun": ["chat", "stream", "embedding", "tts", "asr"],
}


def get_provider_for_task(task: str, preferred: str = "auto") -> str:
    """
    根据任务选择模型提供商
    :param task: 任务类型 chat/stream/embedding/tts/asr
    :param preferred: 用户偏好 auto/deepseek/aliyun
    """
    if preferred != "auto":
        return preferred

    # 语音任务只能用阿里云
    if task in ("tts", "asr"):
        return "aliyun"

    # 嵌入任务优先阿里云
    if task == "embedding":
        return "aliyun"

    # 默认DeepSeek
    return "deepseek"


async def chat_completion(
    messages: List[Dict[str, str]],
    system_prompt: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    provider: str = "auto",
) -> str:
    """统一聊天完成接口"""
    provider = get_provider_for_task("chat", provider)

    try:
        if provider == "aliyun":
            return await qwen_util.chat_completion(
                messages, system_prompt, temperature, max_tokens
            )
        else:
            return await deepseek_util.chat_completion(
                messages, system_prompt, temperature, max_tokens
            )
    except Exception as e:
        logger.error("[%s] Chat失败: %s", provider, e)
        # 故障转移
        fallback = "deepseek" if provider == "aliyun" else "aliyun"
        logger.info("故障转移到 %s", fallback)
        if fallback == "aliyun":
            return await qwen_util.chat_completion(
                messages, system_prompt, temperature, max_tokens
            )
        else:
            return await deepseek_util.chat_completion(
                messages, system_prompt, temperature, max_tokens
            )


async def chat_completion_stream(
    messages: List[Dict[str, str]],
    system_prompt: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    provider: str = "auto",
) -> AsyncGenerator[str, None]:
    """统一流式接口"""
    provider = get_provider_for_task("stream", provider)

    try:
        if provider == "aliyun":
            async for chunk in qwen_util.chat_completion_stream(
                messages, system_prompt, temperature, max_tokens
            ):
                yield chunk
        else:
            async for chunk in deepseek_util.chat_completion_stream(
                messages, system_prompt, temperature, max_tokens
            ):
                yield chunk
    except Exception as e:
        logger.error("[%s] Stream失败: %s", provider, e)
        # 流式不支持故障转移，抛出异常
        raise


async def get_embedding(text: str, provider: str = "auto") -> List[float]:
    """统一嵌入接口"""
    provider = get_provider_for_task("embedding", provider)

    if provider == "aliyun":
        return await qwen_util.get_embedding(text)
    else:
        from backend.utils.embedding_util import get_embedding as _get
        return await _get(text)
