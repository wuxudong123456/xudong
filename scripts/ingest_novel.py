"""
导入四大名著全文到 Milvus 向量库
1. 读取原文 → 2. 语义层级切片 → 3. 批量向量化 → 4. 存入Milvus独立集合

支持：
  - 《西游记》 (xiyou)   — 集合 novel_xiyou
  - 《三国演义》(sanguo)  — 集合 novel_sanguo
  - 《红楼梦》  (honglou) — 集合 novel_honglou
  - 《水浒传》  (shuihu)  — 集合 novel_shuihu

运行: python scripts/ingest_novel.py
      或 python scripts/ingest_novel.py --novel xiyou  (仅处理指定名著)

注意: 四本名著总计约280万字，需调用多次Embedding API，预计耗时30-60分钟
"""
import sys
import os
import asyncio
import argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.text_chunker import chunk_novel, NOVEL_PREFIX
from backend.utils.embedding_util import get_embeddings
from backend.utils.milvus_util import (
    connect_milvus, create_collection, create_index,
    insert_chunks, NOVEL_COLLECTIONS, NOVEL_NAMES_CN,
)

# 批量处理大小 (每批处理的切片数，避免API超时)
BATCH_SIZE = 20

# 四本名著的配置文件
NOVEL_CONFIG = {
    "xiyou": {
        "file": "《西游记》(1).txt",
        "collection": NOVEL_COLLECTIONS["xiyou"],
        "name_cn": "西游记",
        "chunk_config": {"max_chars": 500, "min_chars": 200, "overlap_chars": 50},
    },
    "sanguo": {
        "file": "《三国演义》(1).txt",
        "collection": NOVEL_COLLECTIONS["sanguo"],
        "name_cn": "三国演义",
        "chunk_config": {"max_chars": 500, "min_chars": 200, "overlap_chars": 50},
    },
    "honglou": {
        "file": "《红楼梦》(1).txt",
        "collection": NOVEL_COLLECTIONS["honglou"],
        "name_cn": "红楼梦",
        "chunk_config": {"max_chars": 500, "min_chars": 200, "overlap_chars": 50},
    },
    "shuihu": {
        "file": "《水浒传》(1).txt",
        "collection": NOVEL_COLLECTIONS["shuihu"],
        "name_cn": "水浒传",
        "chunk_config": {"max_chars": 500, "min_chars": 200, "overlap_chars": 50},
    },
}


async def ingest_novel(novel_key: str, base_dir: str) -> int:
    """
    导入单本名著到 Milvus
    :param novel_key: 名著标识 (xiyou/sanguo/honglou/shuihu)
    :param base_dir: 项目根目录
    :return: 导入的切片总数
    """
    config = NOVEL_CONFIG[novel_key]
    file_path = os.path.join(base_dir, config["file"])

    if not os.path.exists(file_path):
        print(f"  [错误] 找不到文件: {file_path}")
        return 0

    print(f"\n{'='*60}")
    print(f"  《{config['name_cn']}》全文导入 Milvus")
    print(f"{'='*60}")

    # 1. 读取原文
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"  [读取] 文件大小: {len(text):,} 字符")

    # 2. 语义层级切片
    print(f"  [切片] 正在进行语义层级切片...")
    cc = config["chunk_config"]
    chunks = chunk_novel(
        text, novel_name=novel_key,
        max_chars=cc["max_chars"], min_chars=cc["min_chars"],
        overlap_chars=cc["overlap_chars"],
    )
    print(f"  [切片] 共生成 {len(chunks)} 个语义块")

    if not chunks:
        print(f"  [警告] 未生成任何切片，跳过")
        return 0

    # 输出前3个切片示例
    print(f"\n  --- 前3个切片示例 ---")
    for i, c in enumerate(chunks[:3]):
        print(f"  [{c['chunk_id']}] 第{c['chapter_num']}回 | {c['chapter_title'][:30]}")
        print(f"    字符数: {c['char_count']} | 内容: {c['content'][:80]}...")

    # 3. 准备 Milvus 集合（重建以导入全新数据）
    collection = create_collection(config["collection"], drop_if_exists=True)
    create_index(collection)

    # 4. 批量向量化 + 插入
    print(f"\n  [向量化] 开始批量处理 (每批{BATCH_SIZE}条)...")
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_idx in range(total_batches):
        start = batch_idx * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(chunks))
        batch_chunks = chunks[start:end]
        texts = [c["content"] for c in batch_chunks]

        print(f"    批次 {batch_idx + 1}/{total_batches}: "
              f"切片 {start+1}-{end}/{len(chunks)}", end="")

        try:
            embeddings = await get_embeddings(texts)
            insert_chunks(collection, batch_chunks, embeddings)
            print(f" [OK] 已插入 {len(batch_chunks)} 条")
        except Exception as e:
            print(f" [FAIL] {e}")
            # 失败后暂停更久再重试
            await asyncio.sleep(5)
            continue

        # 遵守API频率限制
        if batch_idx < total_batches - 1:
            await asyncio.sleep(1)

    print(f"\n  《{config['name_cn']}》导入完成! 集合: {collection.name}, 实体数: {collection.num_entities}")
    return len(chunks)


async def main():
    parser = argparse.ArgumentParser(description="导入四大名著全文到Milvus向量库")
    parser.add_argument("--novel", type=str, default=None,
                        choices=["xiyou", "sanguo", "honglou", "shuihu"],
                        help="仅导入指定名著 (默认导入全部四本)")
    args = parser.parse_args()

    print("=" * 60)
    print("  四大名著全文导入 Milvus 向量库")
    print("  语义层级切片 + 向量相似度精准匹配")
    print("=" * 60)

    # 项目根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 连接 Milvus
    connect_milvus()

    # 确定要导入的名著列表
    if args.novel:
        novel_list = [args.novel]
    else:
        novel_list = ["xiyou", "sanguo", "honglou", "shuihu"]

    total_chunks = 0
    for novel_key in novel_list:
        chunk_count = await ingest_novel(novel_key, base_dir)
        total_chunks += chunk_count

    # 输出总结
    print("\n" + "=" * 60)
    print(f"  全部导入完成!")
    print(f"  总切片数: {total_chunks}")
    print(f"  处理名著: {', '.join(NOVEL_CONFIG[k]['name_cn'] for k in novel_list)}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
