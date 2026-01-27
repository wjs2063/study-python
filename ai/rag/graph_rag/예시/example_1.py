from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()
# 1. Neo4j 연결 설정
graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="MyPassWord@")

# 2. LLM 모델 설정 (추출 시 gpt-4o 등 추론 능력이 좋은 모델 권장)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 3. 사용자 정의 구조 정의 (이 부분이 핵심입니다)
allowed_nodes = ["Person", "Organization", "Technology", "Project"]
allowed_relationships = ["WORKS_AT", "DEVELOPED", "USES", "PARTNER_WITH"]

# 4. Transformer 초기화 (정의한 구조 주입)
transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=allowed_nodes,
    allowed_relationships=allowed_relationships,
    strict_mode=True,  # True로 설정 시, 허용되지 않은 노드/관계는 절대 생성하지 않음
    node_properties=True
)

# 5. 데이터 준비 (PDF에서 추출한 텍스트라고 가정)
text = """
김철수는 삼성전자에서 근무하며, Python과 FastAPI를 사용하여 AI 에이전트 프로젝트를 개발했습니다.
이 프로젝트는 Neo4j 그래프 데이터베이스를 활용합니다.
"""
documents = [Document(page_content=text)]

# 6. 그래프 데이터 추출
graph_documents = transformer.convert_to_graph_documents(documents)
print(graph_documents)
# [GraphDocument(nodes=[Node(id='김철수', type='Person', properties={}), Node(id='삼성전자', type='Organization', properties={}), Node(id='Python', type='Technology', properties={}), Node(id='Fastapi', type='Technology', properties={}), Node(id='Ai 에이전트 프로젝트', type='Project', properties={}), Node(id='Neo4J', type='Technology', properties={})], relationships=[Relationship(source=Node(id='김철수', type='Person', properties={}), target=Node(id='삼성전자', type='Organization', properties={}), type='WORKS_AT', properties={}), Relationship(source=Node(id='김철수', type='Person', properties={}), target=Node(id='Ai 에이전트 프로젝트', type='Project', properties={}), type='DEVELOPED', properties={}), Relationship(source=Node(id='Ai 에이전트 프로젝트', type='Project', properties={}), target=Node(id='Python', type='Technology', properties={}), type='USES', properties={}), Relationship(source=Node(id='Ai 에이전트 프로젝트', type='Project', properties={}), target=Node(id='Fastapi', type='Technology', properties={}), type='USES', properties={}), Relationship(source=Node(id='Ai 에이전트 프로젝트', type='Project', properties={}), target=Node(id='Neo4J', type='Technology', properties={}), type='USES', properties={})], source=Document(metadata={}, page_content='\n김철수는 삼성전자에서 근무하며, Python과 FastAPI를 사용하여 AI 에이전트 프로젝트를 개발했습니다.\n이 프로젝트는 Neo4j 그래프 데이터베이스를 활용합니다.\n'))]
# 7. Neo4j에 저장
graph.add_graph_documents(
    graph_documents,
    baseEntityLabel=True,  # 모든 노드에 공통 라벨 추가 여부
    include_source=True  # 원문 소스 연결 여부
)
