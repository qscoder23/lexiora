"""向量检索模块：FAISS索引构建和相似度查询"""

from langchain_core.documents import Document
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS

from src.config import load_config


def build_documents(items: list[dict], source_type: str = "law") -> list[Document]:
    """将结构化数据转为LangChain Document对象

    Args:
        items: 法规或案例的结构化数据列表
        source_type: "law" 或 "case"

    Returns:
        Document列表，page_content为可检索文本，metadata保留原始字段
    """
    docs = []
    for item in items:
        if source_type == "law":
            content = f"{item['law_name']} {item['article_number']}：{item['content']}"
            metadata = {
                "source_type": "law",
                "law_name": item["law_name"],
                "article_number": item["article_number"],
            }
        else:
            content = f"案例{item['case_id']}：{item['fact']} 判决：{item['judgment']}"
            metadata = {
                "source_type": "case",
                "case_id": item["case_id"],
                "crime": item.get("crime", ""),
            }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


class VectorSearchEngine:
    """向量检索引擎"""

    def __init__(self):
        config = load_config()
        self.embeddings = DashScopeEmbeddings(
            model=config["embedding"]["model"],
            dashscope_api_key=config["embedding"]["api_key"],
        )
        self.vectorstore = None

    def build_index(self, documents: list[Document]) -> None:
        """构建FAISS索引"""
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)

    def save_index(self, path: str) -> None:
        """保存索引到磁盘"""
        if self.vectorstore:
            self.vectorstore.save_local(path)

    def load_index(self, path: str) -> None:
        """从磁盘加载索引"""
        self.vectorstore = FAISS.load_local(
            path, self.embeddings, allow_dangerous_deserialization=True,
        )

    def query(self, query_text: str, top_k: int = 5) -> list[Document]:
        """相似度检索

        Args:
            query_text: 查询文本
            top_k: 返回最相似的K个文档

        Returns:
            相似文档列表
        """
        if not self.vectorstore:
            raise ValueError("索引未构建，请先调用build_index或load_index")
        results = self.vectorstore.similarity_search(query_text, k=top_k)
        return results