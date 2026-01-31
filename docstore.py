import sqlite3
import json


class SimpleDocStore:
    def __init__(self, db_path="docstore.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parent_chunks (
                id TEXT PRIMARY KEY,
                content TEXT
            )
        ''')
        self.conn.commit()

    def save_parents(self, parents: list):
        """批量保存父块"""
        data = [(p['id'], p['content']) for p in parents]
        self.cursor.executemany('INSERT OR REPLACE INTO parent_chunks VALUES (?, ?)', data)
        self.conn.commit()

    def get_parent(self, parent_id: str) -> str:
        """根据ID获取父块内容"""
        self.cursor.execute('SELECT content FROM parent_chunks WHERE id = ?', (parent_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

# 初始化一个全局实例
doc_store = SimpleDocStore()