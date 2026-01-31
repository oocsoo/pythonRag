from typing import List


def split_into_chunks(doc_file: str) -> List[str]:
    """简单的按空行分段（保留向后兼容）"""
    with open(doc_file, "r", encoding="utf-8") as file:
        content = file.read()
    return [chunk for chunk in content.split('\n\n')]
