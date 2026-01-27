import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
load_dotenv()

# 1. PDF 로드 및 청킹
loader = PyMuPDFLoader("lucky_day.pdf")
docs = loader.load()

# 소설은 문맥 연결이 중요하므로 chunk_overlap을 충분히 줍니다.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(docs)

# 2. LLM 및 그래프 설정
llm = ChatOpenAI(model="gpt-4o", temperature=0)
graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="MyPassWord@")

# 3. 소설 전용 스키마 정의
# 노드: 인물, 장소, 중요한 물건, 핵심 사건, 테마(주제)
allowed_nodes = ["Character", "Location", "Object", "Event", "Theme"]
# 관계: 상호작용, 위치함, 소유함, 참여함, 원인이됨
allowed_relationships = ["INTERACTS_WITH", "LOCATED_IN", "OWNS", "PARTICIPATED_IN", "CAUSED"]

# 4. Transformer 설정 (속성 추출 강화)
transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=allowed_nodes,
    allowed_relationships=allowed_relationships,
    strict_mode=True,
    # 소설에서 추출 가능한 구체적인 속성 리스트
    node_properties=["description", "personality", "motivation", "role"]
)

summary_prompt = PromptTemplate.from_template(
    "다음 소설의 한 장면을 읽고, 전체 줄거리 맥락을 파악할 수 있게 1~2문장으로 요약하세요:\n\n{content}"
)
summary_chain = summary_prompt | llm | StrOutputParser()

# 2. 그래프 데이터 추출 및 줄거리 주입 로직
enhanced_graph_docs = []

for doc in chunks:
    # A. 해당 청크의 줄거리 요약 생성
    chunk_summary = summary_chain.invoke({"content": doc.page_content})

    # B. 기본 노드/관계 추출
    graph_doc = transformer.convert_to_graph_documents([doc])[0]

    # C. 추출된 모든 노드에 줄거리 정보 강제 주입
    for node in graph_doc.nodes:
        # 기존 properties 유지하며 summary 추가
        node.properties["chunk_summary"] = chunk_summary
        # 노드의 역할(Role)이나 중요도도 여기서 추가 정의 가능

    enhanced_graph_docs.append(graph_doc)
graph.add_graph_documents(enhanced_graph_docs, baseEntityLabel=True, include_source=True)


graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="MyPassWord@")

# 2. Full-text 인덱스 생성 (이 코드를 hybrid_db 생성 전에 넣으세요)
# 'entity_fulltext_index'라는 이름으로 __Entity__ 라벨의 'id' 속성을 인덱싱합니다.
graph.query("""
CREATE FULLTEXT INDEX entity_fulltext_index IF NOT EXISTS 
FOR (n:__Entity__) ON EACH [n.id]
""")

print("✅ Full-text 인덱스 생성 완료")