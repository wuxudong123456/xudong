"""
DeepSeek Chat 客户端工具
统一封装 DeepSeek API 调用 (OpenAI 兼容格式)
支持普通对话和 Function Calling
"""
import httpx
from typing import List, Dict, Optional, AsyncGenerator
from backend.config import settings


async def chat_completion(
    messages: List[Dict[str, str]],
    system_prompt: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> str:
    """
    调用 DeepSeek Chat API 获取回复
    :param messages: 对话消息列表 [{"role":"user","content":"..."}]
    :param system_prompt: 系统提示词（角色设定）
    :param temperature: 生成温度 (0-2)
    :param max_tokens: 最大生成token数
    :return: 模型回复文本
    """
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
            json={
                "model": settings.DEEPSEEK_MODEL,
                "messages": full_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def chat_completion_stream(
    messages: List[Dict[str, str]],
    system_prompt: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> AsyncGenerator[str, None]:
    """
    流式调用 DeepSeek Chat API
    :param messages: 对话消息列表
    :param system_prompt: 系统提示词
    :param temperature: 生成温度
    :param max_tokens: 最大token数
    :yield: 逐步返回生成的文本片段
    """
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
            json={
                "model": settings.DEEPSEEK_MODEL,
                "messages": full_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            },
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    import json
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue


async def chat_with_functions(
    messages: List[Dict[str, str]],
    functions: List[Dict],
    system_prompt: str = None,
) -> Dict:
    """
    Function Calling 模式调用 DeepSeek
    :param messages: 对话消息
    :param functions: 函数定义列表 (OpenAI JSON Schema格式)
    :param system_prompt: 系统提示词
    :return: 模型返回的函数调用或文本回复
    """
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
            json={
                "model": settings.DEEPSEEK_MODEL,
                "messages": full_messages,
                "temperature": 0.3,
                "tools": functions,
                "tool_choice": "auto",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        choice = data["choices"][0]
        if choice["finish_reason"] == "tool_calls":
            return {"type": "function_call", "calls": choice["message"].get("tool_calls", [])}
        return {"type": "text", "content": choice["message"]["content"]}
