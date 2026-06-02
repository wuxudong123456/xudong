
"""
数据入库主脚本：1. 段落切片入库  2. QA 对生成入库
用法: python ingest.py [--skip-qa] [--skip-chunks]
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingestion.chunker import Chunker
from ingestion.milvus_store import Store
from ingestion.qa_generator import QAGenerator
from config import FILE_CHUNKS_COLLECTION, QA_PAIRS_COLLECTION


def main():
    parser = argparse.ArgumentParser(description="三国演义 RAG 数据入库")
    parser.add_argument("--skip-chunks", action="store_true", help="跳过文件切片入库")
    parser.add_argument("--skip-qa", action="store_true", help="跳过 QA 对生成入库")
    parser.add_argument("--qa-samples", type=int, default=3, help="每章回生成的问答对数（默认3）")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    txt_path = os.path.join(base_dir, "《三国演义》(1).txt")

    store = Store()

    # ---- Step 1: 文件切片 ----
    if not args.skip_chunks:
        print("=" * 50)
        print("Step 1: 文件切片入库")
        print("=" * 50)

        chunker = Chunker(txt_path)
        chunks = chunker.parse()
        print(f"解析完成: {len(chunks)} 个段落切片")

        store.create_file_chunks_collection()
        store.insert_file_chunks(chunks)

        # 验证
        stats = store.client.get_collection_stats(FILE_CHUNKS_COLLECTION)
        print(f"file_chunks 集合行数: {stats.get('row_count', 'N/A')}")

        # 手动 load 以便查询
        store.client.load_collection(FILE_CHUNKS_COLLECTION)
        print("file_chunks 加载完成，可进行检索")
    else:
        # 确保加载
        if store.client.has_collection(FILE_CHUNKS_COLLECTION):
            store.client.load_collection(FILE_CHUNKS_COLLECTION)

    # ---- Step 2: QA 对生成 ----
    if not args.skip_qa:
        print()
        print("=" * 50)
        print("Step 2: QA 对生成入库")
        print("=" * 50)

        # 重新读取切片用于生成
        chunker = Chunker(txt_path)
        chunks = chunker.parse()

        generator = QAGenerator()
        qa_pairs = generator.generate_for_chunks(chunks, samples_per_chapter=args.qa_samples)

        if not qa_pairs:
            print("警告：未生成任何问答对，请检查 DeepSeek API 连接")
        else:
            store.create_qa_pairs_collection()
            store.insert_qa_pairs(qa_pairs)

            stats = store.client.get_collection_stats(QA_PAIRS_COLLECTION)
            print(f"qa_pairs 集合行数: {stats.get('row_count', 'N/A')}")

            store.client.load_collection(QA_PAIRS_COLLECTION)
            print("qa_pairs 加载完成，可进行检索")
    else:
        if store.client.has_collection(QA_PAIRS_COLLECTION):
            store.client.load_collection(QA_PAIRS_COLLECTION)

    print()
    print("=" * 50)
    print("数据入库完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
