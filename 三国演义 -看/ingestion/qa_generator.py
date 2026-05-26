"""
调用 DeepSeek API 从《三国演义》段落自动生成问答对
"""
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

QA_PROMPT = """你是一位精通《三国演义》的国学老师。请根据以下段落内容，生成 3 个高质量的问答对。

要求：
1. 问题覆盖人物、事件、成语典故等
2. 答案准确引用原文内容
3. 返回严格 JSON 格式：{{"qa_pairs": [{{"question": "...", "answer": "..."}}]}}

段落内容：
{content}

请直接返回 JSON，不要有任何其他文字。"""


class QAGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )

    def generate(self, content: str) -> list[dict]:
        """基于单段文本生成问答对"""
        # 截断过长文本，避免 token 超限
        content = content[:2000]
        prompt = QA_PROMPT.format(content=content)

        response = self.client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )

        raw = response.choices[0].message.content.strip()
        # 清理可能的 markdown 标记
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        import json
        try:
            data = json.loads(raw)
            return data.get("qa_pairs", [])
        except json.JSONDecodeError:
            print(f"JSON 解析失败，原始返回: {raw[:200]}")
            return []

    def generate_for_chunks(
        self,
        chunks: list[dict],
        samples_per_chapter: int = 3,
    ) -> list[dict]:
        """为所有切片生成问答对，每章回取若干个代表性段落"""
        # 按章回分组，跳过纯诗词/短段落
        by_chapter: dict[int, list[dict]] = {}
        for chunk in chunks:
            num = chunk["chapter_num"]
            if num not in by_chapter:
                by_chapter[num] = []
            if len(chunk["content"]) > 100:
                by_chapter[num].append(chunk)

        all_qa = []
        for chapter_num, chapter_chunks in sorted(by_chapter.items()):
            # 每章取前 N 个较长的段落
            candidates = sorted(chapter_chunks, key=lambda c: len(c["content"]), reverse=True)
            selected = candidates[:samples_per_chapter]

            print(f"第 {chapter_num} 回：为 {len(selected)} 个段落生成问答对...")
            for chunk in selected:
                qa_pairs = self.generate(chunk["content"])
                for qa in qa_pairs:
                    qa["source_chapter"] = chapter_num
                    qa["source_chunk_id"] = 0  # 后续可改进
                all_qa.extend(qa_pairs)

        print(f"共生成 {len(all_qa)} 条问答对")
        return all_qa
