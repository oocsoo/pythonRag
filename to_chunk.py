import uuid
from typing import List, Dict, Tuple
# 导入同目录下的 data_loader
from data_loader import loader


class ParentChildSplitter:
    def __init__(self, parent_size: int = 800, child_size: int = 200, overlap: int = 50):
        """
        初始化切分器
        :param parent_size: 父块大小 (字符数)，用于 LLM 上下文
        :param child_size: 子块大小 (字符数)，用于向量检索
        :param overlap: 滑动窗口重叠部分
        """
        self.parent_size = parent_size
        self.child_size = child_size
        self.overlap = overlap

    def _split_text_window(self, text: str, chunk_size: int) -> List[str]:
        """
        辅助函数：基于字符数的滑动窗口切分
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk = text[start:end]

            # 只有当切分出来的块长度有意义时才添加
            if len(chunk.strip()) > 5:
                chunks.append(chunk)

            # 如果已经到了末尾，跳出
            if end == text_len:
                break

            start += (chunk_size - self.overlap)

        return chunks

    def split_main(self, doc_file: str) -> Tuple[List[Dict], List[Dict]]:
        """
        主入口：读取文件 -> 切分父块 -> 切分子块
        :return: (parents 列表, children 列表)
        """
        print(f"1. [ToChunk] 正在加载文件: {doc_file}")

        # 1. 使用 Loader 读取文件内容 (自动识别 PDF/Word/Excel)
        full_text = loader.load(doc_file)

        if not full_text:
            print("   [警告] 文件内容为空或读取失败。")
            return [], []

        parents = []
        children = []

        # 2. 预处理：先按自然段落（换行符）粗分
        # 这一步是为了防止一个父块横跨两个完全不相关的段落
        # 清洗掉过多的空行
        raw_paragraphs = [p for p in full_text.split('\n') if p.strip()]

        print(f"   - 原始文本已读取，包含 {len(full_text)} 字符")

        for para in raw_paragraphs:
            # 如果段落太短，直接忽略（比如页码、杂乱符号）
            if len(para) < 10:
                continue

            # 3. 生成父块 (Parent Chunks)
            # 如果段落很长，会对段落再进行窗口切分；如果段落短于 parent_size，它本身就是一个父块
            if len(para) > self.parent_size:
                p_chunks_text = self._split_text_window(para, self.parent_size)
            else:
                p_chunks_text = [para]

            for p_content in p_chunks_text:
                # 生成唯一的父ID
                p_id = str(uuid.uuid4())

                parents.append({
                    "id": p_id,
                    "content": p_content,
                    "source": doc_file  # 可选：记录来源文件
                })

                # 4. 生成子块 (Child Chunks)
                # 子块是基于当前父块的内容切分的
                c_chunks_text = self._split_text_window(p_content, self.child_size)

                for c_content in c_chunks_text:
                    children.append({
                        "id": str(uuid.uuid4()),
                        "content": c_content,
                        "parent_id": p_id,  # 关键：链接回父ID
                        "source": doc_file
                    })

        return parents, children


# 实例化单例，供 emb_save_db.py 调用
splitter = ParentChildSplitter(parent_size=800, child_size=200, overlap=50)
