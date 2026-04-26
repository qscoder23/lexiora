"""将示例数据导入Neo4j知识图谱"""
from src.data.collector import load_sample_laws, load_sample_cases
from src.data.kg_builder import build_knowledge_graph

laws = load_sample_laws()
cases = load_sample_cases()
stats = build_knowledge_graph(laws, cases)
print(f"导入完成: {stats}")