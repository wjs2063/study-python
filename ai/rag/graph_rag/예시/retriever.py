from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_neo4j import Neo4jVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# 1. 벡터 인덱스 연결
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_index = Neo4jVector.from_existing_graph(
    embeddings,
    url="bolt://localhost:7687",
    username="neo4j",
    password="MyPassWord@",
    index_name="entity_index",
    node_label="__Entity__",  # Person 대신 공통 라벨 사용
    text_node_properties=["id"], # Transformer의 기본값인 id 확인 필요
    embedding_node_property="embedding"
)
from langchain_neo4j import Neo4jGraph
graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="MyPassWord@")

# 2. 그래프 컨텍스트를 추출하는 함수 (Cypher 사용)
def get_hybrid_context(query_results):
    if not query_results:
        return ""

    all_paths = []
    visited_nodes = set()

    for doc in query_results:
        raw_id = doc.metadata.get('id') or doc.page_content
        entity_id = raw_id.replace("id: ", "").strip()

        if entity_id in visited_nodes: continue
        visited_nodes.add(entity_id)

        # 쿼리 수정: 경로(path)를 관계 단위로 쪼개서(UNWIND) 각 노드의 ID를 직접 반환
        cypher_query = """
        MATCH p = (e)-[r*1..2]-(neighbor)
        WHERE toLower(e.id) = toLower($entity_id) OR toLower(e.name) = toLower($entity_id)
        WITH p
        UNWIND relationships(p) AS rel
        RETURN 
            startNode(rel).id AS source, 
            type(rel) AS rel_type, 
            endNode(rel).id AS target
        LIMIT 20
        """

        print(f"🔍 DB 검색 시도 ID: '{entity_id}'")
        paths_data = graph.query(cypher_query, params={"entity_id": entity_id})

        if not paths_data:
            print(f"⚠️ '{entity_id}' 노드와 연결된 관계가 없습니다.")
            continue

        # 경로 조각들을 모아서 문장 생성
        current_path_segments = []
        for row in paths_data:
            source = row['source']
            rel_type = row['rel_type']
            target = row['target']
            current_path_segments.append(f"({source})-[:{rel_type}]->({target})")

        all_paths.append(" / ".join(current_path_segments))
        print(all_paths)
    return "\n".join(list(set(all_paths)))

from pydantic import BaseModel, Field
class Entities(BaseModel):
    names: list[str] = Field(description="질문에서 언급된 주요 인물, 기술, 조직명 리스트")


extraction_llm = ChatOpenAI(model="gpt-4o", temperature=0)
entity_extractor = extraction_llm.with_structured_output(Entities)


def smart_retriever(question):
    # 1. 질문에서 키워드 추출
    extracted = entity_extractor.invoke(f"다음 질문에서 지식 그래프 검색을 위한 핵심 키워드를 추출하세요: {question}")

    # 2. 추출된 키워드별로 그래프 컨텍스트 수집
    final_contexts = []
    for name in extracted.names:
        # 벡터 검색 없이 바로 Cypher로 노드를 찾아도 됩니다 (정확한 매칭 시)
        # 여기서는 기존 방식대로 검색 결과를 활용
        res = vector_index.similarity_search(name, k=1)
        final_contexts.append(get_hybrid_context(res))

    return "\n".join(final_contexts)

# 3. RAG 체인 구성
llm = ChatOpenAI(model="gpt-4o", temperature=0)

template = """당신은 지식 그래프 기반의 전문 답변가입니다.
제공된 '그래프 컨텍스트'만을 사용하여 질문에 답하세요. 
답을 모른다면 모른다고 하세요.

그래프 컨텍스트:
{context}

질문: {question}
답변:"""

prompt = ChatPromptTemplate.from_template(template)

# 체인 정의
chain = (
    {
        "context": RunnablePassthrough() | smart_retriever, # 질문에서 바로 엔티티 추출 및 검색
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

# 실행
response = chain.invoke("김철수의 업무 내용과 사용 기술을 알려줘")

print(response)