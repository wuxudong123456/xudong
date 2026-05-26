"""
文本切片器：将《三国演义》按 <p> 段落切分
"""
import re
import os


class Chunker:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> list[dict]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"文件不存在: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 按章回分割
        pattern = r"([第][零一二三四五六七八九十百]+[回]\s+.+?)(?=[第][零一二三四五六七八九十百]+[回]|$)"
        chunks: list[dict] = []

        for match in re.finditer(pattern, content, re.DOTALL):
            chapter_text = match.group(1).strip()
            if not chapter_text:
                continue

            # 提取标题
            title_match = re.match(r"([第][零一二三四五六七八九十百]+[回]\s+.+)", chapter_text)
            if title_match:
                title = title_match.group(1).strip()
                body = chapter_text[len(title):].strip()
            else:
                title = chapter_text[:50]
                body = chapter_text

            chapter_num = self._extract_chapter_num(title)
            paragraphs = self._split_paragraphs(body)

            for idx, para in enumerate(paragraphs):
                para = self._clean(para)
                if len(para) < 20:  # 跳过太短的段落（诗词、标题等）
                    continue
                chunks.append({
                    "chapter_num": chapter_num,
                    "title": title,
                    "chunk_index": idx,
                    "content": para,
                })

        print(f"共解析 {len(set(c['chapter_num'] for c in chunks))} 章回，"
              f"{len(chunks)} 个有效段落切片")
        return chunks

    def _split_paragraphs(self, text: str) -> list[str]:
        parts = re.split(r"<p>\s*</p>|<p>|</p>", text)
        return [p.strip() for p in parts if p.strip()]

    def _clean(self, text: str) -> str:
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"<br\s*/?>", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_chapter_num(self, title: str) -> int:
        num_map = {
            "零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
            "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
            "十": 10, "百": 100,
        }
        m = re.search(r"第([零一二三四五六七八九十百]+)回", title)
        if not m:
            return 0
        chars = m.group(1)
        result = 0
        temp = 0
        for c in chars:
            if c == "十":
                temp = (temp if temp > 0 else 1) * 10
            elif c == "百":
                temp = (temp if temp > 0 else 1) * 100
            else:
                temp += num_map[c]
            result = temp
        return result
