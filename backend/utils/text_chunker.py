"""
文本切片工具
将四大名著长文本按语义层级切分为适合向量化的短块
策略: 按章节分割 → 按完整句子边界切分 → 每块300-500字符 → 50字符重叠
核心原则: 以完整语义段落为最小切割单元，禁止割裂语句内容
"""
import re
from typing import List, Dict

# 四大名著对应的 chunk_id 前缀
NOVEL_PREFIX = {
    "xiyou": "xy",      # 西游记
    "sanguo": "sg",     # 三国演义
    "honglou": "hl",    # 红楼梦
    "shuihu": "sh",     # 水浒传
}

# 四大名著对应的 Milvus 集合名
NOVEL_COLLECTION = {
    "xiyou": "novel_xiyou",
    "sanguo": "novel_sanguo",
    "honglou": "novel_honglou",
    "shuihu": "novel_shuihu",
}


def split_by_chapter(text: str) -> List[Dict[str, str]]:
    """
    按章节标题分割全文
    支持多种章节格式:
      - "第一回 标题" (三国演义/红楼梦)
      - "第1回:标题" (水浒传)
      - "第X回：标题" (西游记)
      - "第一回  标题" (红楼梦，多空格/全角空格)
    :param text: 小说全文原始文本
    :return: [{chapter_num, title, content}, ...]
    """
    # 正则匹配章节标题：兼容中文数字+阿拉伯数字，冒号/空格/全角空格分隔
    chapter_head = r'第[一二三四五六七八九十百千\d]+回'
    # 用于 split 的模式：匹配整个章节标题行
    split_pattern = r'(' + chapter_head + r'.+?(?:\n|$))'
    # 用于提取标题的模式
    title_pattern = r'(' + chapter_head + r')\s*[：:\s]\s*(.+?)(?=\n|$)'

    chapters = []
    parts = re.split(split_pattern, text)

    chapter_num = 0
    chapter_title = "序言"
    chapter_content = ""

    for part in parts:
        if not part:
            continue
        match = re.match(title_pattern, part.strip())
        if match:
            if chapter_content.strip():
                chapters.append({
                    "chapter_num": chapter_num,
                    "title": chapter_title,
                    "content": chapter_content.strip(),
                })
            chapter_num += 1
            chapter_title = match.group(0).strip()
            chapter_content = ""
        else:
            chapter_content += part

    # 保存最后一章
    if chapter_content.strip():
        chapters.append({
            "chapter_num": chapter_num,
            "title": chapter_title,
            "content": chapter_content.strip(),
        })

    return chapters


def chinese_char_count(text: str) -> int:
    """计算文本中中文字符数量（用于估算token）"""
    return len(re.findall(r'[一-鿿]', text))


def semantic_chunk(text: str, max_chars: int = 500, min_chars: int = 200,
                   overlap_chars: int = 50) -> List[str]:
    """
    将文本按语义边界切分为小块
    以完整语义段落为最小切割单元，禁止割裂语句内容
    分割点: 句号、问号、感叹号、分号、省略号、右引号+句号
    :param text: 输入文本
    :param max_chars: 每块最大字符数
    :param min_chars: 每块最小字符数
    :param overlap_chars: 相邻块重叠字符数（保证语义连贯性）
    :return: 文本块列表
    """
    # 按完整句子边界拆分（包括中文标点和引号结束后的句号）
    sentences = re.split(r'(?<=[。！？；…\.\!\?\;\n\)》）])', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_chunk = ""
    last_overlap = ""

    for sentence in sentences:
        # 如果加入当前句子后超过最大长度，保存当前块
        if current_chunk and len(current_chunk) + len(sentence) > max_chars:
            if len(current_chunk) >= min_chars:
                chunks.append(current_chunk.strip())
                # 保留尾部overlap_chars字符作为下一块的开头（保证语义连贯）
                if overlap_chars > 0 and len(current_chunk) > overlap_chars:
                    last_overlap = current_chunk[-overlap_chars:]
                else:
                    last_overlap = ""
                current_chunk = last_overlap + sentence
            else:
                # 当前块太短，先强制保存再开始新块（防止无限增长）
                chunks.append(current_chunk.strip())
                current_chunk = sentence
        else:
            current_chunk += sentence

    # 处理剩余内容
    if current_chunk.strip():
        if len(current_chunk) < min_chars and chunks:
            # 过短的剩余内容合并到最后一块，不浪费语义信息
            chunks[-1] += current_chunk
        else:
            chunks.append(current_chunk.strip())

    return chunks


def clean_novel_text(text: str) -> str:
    """
    清理小说文本：去除声明信息、HTML标签、规范化空白
    :param text: 原始文本
    :return: 清理后的文本
    """
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 去除常见的电子书声明行
    lines = text.split('\n')
    cleaned_lines = []
    skip_patterns = [
        r'本书由.*搜集整理', r'声明：.*', r'敬告：.*',
        r'更多精彩书籍.*', r'版权归作者.*',
        r'请在下载后.*删除', r'不得用于商业用途',
    ]
    for line in lines:
        should_skip = False
        for pat in skip_patterns:
            if re.search(pat, line):
                should_skip = True
                break
        if not should_skip:
            cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)

    # 规范化空白
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text


def chunk_novel(text: str, novel_name: str = "xiyou",
                max_chars: int = 500, min_chars: int = 200,
                overlap_chars: int = 50) -> List[Dict]:
    """
    处理整本小说: 清理 → 分章 → 语义切块 → 标注元数据
    :param text: 小说全文
    :param novel_name: 小说标识 (xiyou/sanguo/honglou/shuihu)
    :param max_chars: 每块最大字符数
    :param min_chars: 每块最小字符数
    :param overlap_chars: 重叠字符数（保持语义连贯）
    :return: [{chunk_id, novel_name, chapter_num, chapter_title, content, char_count}, ...]
    """
    prefix = NOVEL_PREFIX.get(novel_name, "xx")

    # 预处理
    text = clean_novel_text(text)

    # 分章
    chapters = split_by_chapter(text)
    all_chunks = []
    chunk_idx = 0

    for chapter in chapters:
        chunks = semantic_chunk(
            chapter["content"],
            max_chars=max_chars,
            min_chars=min_chars,
            overlap_chars=overlap_chars,
        )
        for chunk_text in chunks:
            all_chunks.append({
                "chunk_id": f"{prefix}_{chunk_idx:05d}",
                "novel_name": novel_name,
                "chapter_num": chapter["chapter_num"],
                "chapter_title": chapter["title"],
                "content": chunk_text,
                "char_count": chinese_char_count(chunk_text),
            })
            chunk_idx += 1

    return all_chunks
