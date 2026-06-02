# Phase 2: 阿里云API接入 实施计划

> **Goal:** 建立双模型能力，接入阿里云语音服务
> **Architecture:** 统一LLM路由层 + 阿里云专用客户端
> **Tech Stack:** httpx, DashScope API, 阿里云语音服务

---

## 阿里云API信息

- **Base URL**: `https://dashscope.aliyuncs.com/api/v1`
- **API Key**: `sk-390ad1d2d9254ae1ab416df1da7f55ae`
- **可用模型**:
  - `qwen-turbo` / `qwen-plus` / `qwen-max` (文本生成)
  - `qwen-audio-asr` (语音识别)
  - `sambert-zhichu` (语音合成)
  - `text-embedding-v3` (向量嵌入，768维)

---

## 文件变更总览

| 操作 | 文件 | 说明 |
|------|------|------|
| 新建 | `backend/utils/qwen_util.py` | 阿里云LLM封装 |
| 新建 | `backend/utils/tts_util.py` | 语音合成封装 |
| 新建 | `backend/utils/asr_util.py` | 语音识别封装 |
| 新建 | `backend/utils/llm_router.py` | 统一模型路由 |
| 修改 | `backend/config.py` | 阿里云配置 |
| 修改 | `backend/utils/deepseek_util.py` | 兼容统一接口 |

---

## Task 1: 阿里云配置扩展

**Files:**
- 修改: `backend/config.py`

**Step 1: 增加阿里云配置项**

```python
# backend/config.py 中 Settings 类增加

    # 阿里云DashScope配置
    ALIYUN_API_KEY: str = Field(default="", alias="ALIYUN_API_KEY")
    ALIYUN_BASE_URL: str = Field(default="https://dashscope.aliyuncs.com/api/v1", alias="ALIYUN_BASE_URL")
    
    # 阿里云模型选择
    ALIYUN_CHAT_MODEL: str = Field(default="qwen-turbo", alias="ALIYUN_CHAT_MODEL")
    ALIYUN_EMBEDDING_MODEL: str = Field(default="text-embedding-v3", alias="ALIYUN_EMBEDDING_MODEL")
    
    # 语音配置
    ALIYUN_TTS_MODEL: str = Field(default="sambert-zhichu", alias="ALIYUN_TTS_MODEL")
    ALIYUN_ASR_MODEL: str = Field(default="qwen-audio-asr", alias="ALIYUN_ASR_MODEL")
```

---

## Task 2: 阿里云LLM封装

**Files:**
- 新建: `backend/utils/qwen_util.py`

**Step 1: 实现阿里云LLM客户端**

```python
# backend/utils/qwen_util.py
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

logger = logging.getLogger("ai")


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

    logger.info("[Aliyun] Chat请求 model=%s messages=%d", model, len(full_messages))
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.ALIYUN_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        logger.info("[Aliyun] Chat响应 tokens=%s", data.get("usage", {}))
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

    logger.info("[Aliyun] Stream请求 model=%s", model)
    
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

    logger.info("[Aliyun] Embedding请求 model=%s", model)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.ALIYUN_BASE_URL}/embeddings",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        embedding = data["output"]["embeddings"][0]["embedding"]
        logger.info("[Aliyun] Embedding响应 dim=%d", len(embedding))
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

    logger.info("[Aliyun] Batch Embedding请求 model=%s count=%d", model, len(texts))
    
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
```

---

## Task 3: 语音合成(TTS)封装

**Files:**
- 新建: `backend/utils/tts_util.py`

**Step 1: 实现TTS客户端**

```python
# backend/utils/tts_util.py
"""
阿里云语音合成(TTS)封装
将文本转为语音，支持多种音色
"""
import httpx
import base64
import logging
from typing import Optional
from backend.config import settings

logger = logging.getLogger("ai")


async def text_to_speech(
    text: str,
    voice: str = "zhichu",
    format: str = "mp3",
    sample_rate: int = 16000,
) -> Optional[bytes]:
    """
    文本转语音
    :param text: 要合成的文本 (最长300字符)
    :param voice: 音色名称
    :param format: 音频格式 mp3/pcm/wav
    :param sample_rate: 采样率
    :return: 音频二进制数据
    """
    if len(text) > 300:
        text = text[:300]  # 截断
        logger.warning("TTS文本超过300字符，已截断")

    headers = {
        "Authorization": f"Bearer {settings.ALIYUN_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": settings.ALIYUN_TTS_MODEL,
        "input": {"text": text},
        "parameters": {
            "voice": voice,
            "format": format,
            "sample_rate": sample_rate,
        },
    }

    logger.info("[TTS] 合成请求 text=%d字符 voice=%s", len(text), voice)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.ALIYUN_BASE_URL}/audio/speech",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        
        if "audio" in data:
            audio_data = base64.b64decode(data["audio"])
            logger.info("[TTS] 合成成功 audio=%d字节", len(audio_data))
            return audio_data
        else:
            logger.error("[TTS] 合成失败: %s", data)
            return None


async def text_to_speech_url(
    text: str,
    voice: str = "zhichu",
) -> Optional[str]:
    """
    文本转语音，返回临时URL
    用于前端直接播放
    """
    audio_data = await text_to_speech(text, voice)
    if not audio_data:
        return None
    
    # 保存到上传目录，返回URL
    import uuid
    from pathlib import Path
    
    upload_dir = Path(settings.UPLOAD_DIR) / "tts"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = upload_dir / filename
    filepath.write_bytes(audio_data)
    
    return f"/uploads/tts/{filename}"
```

---

## Task 4: 语音识别(ASR)封装

**Files:**
- 新建: `backend/utils/asr_util.py`

**Step 1: 实现ASR客户端**

```python
# backend/utils/asr_util.py
"""
阿里云语音识别(ASR)封装
将语音转为文本
"""
import httpx
import base64
import logging
from typing import Optional
from backend.config import settings

logger = logging.getLogger("ai")


async def speech_to_text(
    audio_data: bytes,
    format: str = "mp3",
    sample_rate: int = 16000,
) -> Optional[str]:
    """
    语音转文本
    :param audio_data: 音频二进制数据
    :param format: 音频格式
    :param sample_rate: 采样率
    :return: 识别出的文本
    """
    audio_base64 = base64.b64encode(audio_data).decode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {settings.ALIYUN_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": settings.ALIYUN_ASR_MODEL,
        "input": {
            "audio": audio_base64,
            "format": format,
            "sample_rate": sample_rate,
        },
    }

    logger.info("[ASR] 识别请求 audio=%d字节", len(audio_data))
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.ALIYUN_BASE_URL}/audio/transcriptions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        
        text = data.get("text", "")
        logger.info("[ASR] 识别结果: %s", text[:50])
        return text if text else None
```

---

## Task 5: 统一模型路由

**Files:**
- 新建: `backend/utils/llm_router.py`

**Step 1: 实现智能路由**

```python
# backend/utils/llm_router.py
"""
统一LLM路由层
自动选择DeepSeek或阿里云，支持故障转移
"""
import logging
from typing import List, Dict, Optional, AsyncGenerator
from backend.config import settings
from backend.utils import deepseek_util, qwen_util

logger = logging.getLogger("ai")

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
```

---

## 验证清单

- [ ] 阿里云chat_completion正常返回
- [ ] 阿里云chat_completion_stream正常流式返回
- [ ] 阿里云embedding返回768维向量
- [ ] TTS合成成功并保存音频文件
- [ ] ASR识别成功返回文本
- [ ] 故障转移机制正常工作
- [ ] 统一路由接口与DeepSeek兼容
