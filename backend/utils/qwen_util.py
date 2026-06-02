"""
阿里云通义千问API封装
支持普通对话、流式对话、嵌入向量
与DeepSeek API保持接口一致
"""
import httpx
import json
import logging
from typing import List, Dict, Optional, AsyncGenerator
from backend.config import settings

logger = logging.getLogger("qwen")


async def chat_completion(
    messages: List[Dict[str, str]],
    system_prompt: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    model: str = None,
) -> str:
    """
    调用阿里云通义千问API
    接口与DeepSeek保持一致
    """
    model = model or settings.ALIYUN_CHAT_MODEL

    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    headers = {
        "Authorization": f"Bearer {settings.ALIYUN_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": full_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    logger.info("Chat请求 model=%s messages=%d", model, len(full_messages))

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.ALIYUN_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        logger.info("Chat响应 tokens=%s", data.get("usage", {}))
        return content


async def chat_completion_stream(
    messages: List[Dict[str, str]],
    system_prompt: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    model: str = None,
) -> AsyncGenerator[str, None]:
    """流式调用阿里云API"""
    model = model or settings.ALIYUN_CHAT_MODEL

    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    headers = {
        "Authorization": f"Bearer {settings.ALIYUN_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": full_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    logger.info("Stream请求 model=%s", model)

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{settings.ALIYUN_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue


async def get_embedding(text: str, model: str = None) -> List[float]:
    """
    调用阿里云嵌入模型
    text-embedding-v3 输出768维
    """
    model = model or settings.ALIYUN_EMBEDDING_MODEL

    headers = {
        "Authorization": f"Bearer {settings.ALIYUN_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "input": {"texts": [text]},
        "parameters": {"text_type": "query"},
    }

    logger.info("Embedding请求 model=%s", model)

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.ALIYUN_BASE_URL}/embeddings",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        embedding = data["output"]["embeddings"][0]["embedding"]
        logger.info("Embedding响应 dim=%d", len(embedding))
        return embedding


async def get_embeddings(texts: List[str], model: str = None) -> List[List[float]]:
    """批量获取嵌入向量"""
    model = model or settings.ALIYUN_EMBEDDING_MODEL

    headers = {
        "Authorization": f"Bearer {settings.ALIYUN_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "input": {"texts": texts},
        "parameters": {"text_type": "document"},
    }

    logger.info("Batch Embedding请求 model=%s count=%d", model, len(texts))

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.ALIYUN_BASE_URL}/embeddings",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        embeddings = [e["embedding"] for e in data["output"]["embeddings"]]
        return embeddings
