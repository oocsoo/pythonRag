import os
import pandas as pd
from pypdf import PdfReader
from docx import Document


class DataLoader:
    def load(self, file_path: str) -> str:
        """
        统一加载入口：根据文件扩展名自动选择读取方式
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 获取文件后缀名 (转小写)
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == '.pdf':
                return self._read_pdf(file_path)
            elif ext in ['.docx', '.doc']:
                return self._read_word(file_path)
            elif ext in ['.xlsx', '.xls', '.csv']:
                return self._read_excel(file_path)
            elif ext in ['.txt', '.md', '.py', '.json', '.js', '.html']:
                return self._read_text(file_path)
            else:
                print(f"警告: 不支持的文件格式 {ext}，尝试以纯文本读取...")
                return self._read_text(file_path)
        except Exception as e:
            print(f"文件读取失败 [{file_path}]: {e}")
            return ""

    def _read_text(self, path):
        """读取纯文本文件"""
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _read_pdf(self, path):
        """读取 PDF (提取文字)"""
        text = ""
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"PDF 解析错误: {e}")
        return text

    def _read_word(self, path):
        """读取 Word 文档"""
        try:
            doc = Document(path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Word 解析错误: {e}")
            return ""

    def _read_excel(self, path):
        """读取 Excel/CSV，将每一行序列化为文本"""
        text = ""
        try:
            if path.endswith('.csv'):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)

            # 遍历每一行，将其转换为 "列名:值, 列名:值" 的格式
            for _, row in df.iterrows():
                row_str_list = []
                for col in df.columns:
                    val = row[col]
                    if pd.notna(val):  # 跳过空值
                        row_str_list.append(f"{col}: {val}")
                if row_str_list:
                    text += ", ".join(row_str_list) + "\n"
        except Exception as e:
            print(f"Excel 解析错误: {e}")
        return text


# 实例化一个全局加载器供外部调用
loader = DataLoader()