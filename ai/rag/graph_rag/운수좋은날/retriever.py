from langchain_neo4j import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)
graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="MyPassWord@")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
hybrid_db = Neo4jVector.from_existing_index(
    embeddings,
    url="bolt://localhost:7687",
    username="neo4j",
    password="MyPassWord@",
    index_name="entity_index",
    keyword_index_name="entity_fulltext_index",
    search_type="hybrid"
)
# K=3 정도로 설정하여 가장 연관성 높은 엔티티를 타겟팅합니다.
hybrid_retriever = hybrid_db.as_retriever(search_kwargs={"k": 3})


# 2. 질문에서 검색용 엔티티를 추출하는 스키마
class Entities(BaseModel):
    names: list[str] = Field(description="질문에서 언급된 주요 인물, 사물, 사건 키워드 리스트")


entity_extractor = ChatOpenAI(model="gpt-4o", temperature=0).with_structured_output(Entities)


# 3. 그래프 문맥 추출 함수 (chunk_summary 포함)
def get_enhanced_context(query_results):
    if not query_results: return ""

    all_relationships = []
    visited_nodes = set()

    for doc in query_results:
        # 노드 ID 추출 (id 속성 우선)
        entity_id = doc.metadata.get('id') or doc.page_content
        entity_id = entity_id.replace("id: ", "").strip()
        if entity_id in visited_nodes: continue
        visited_nodes.add(entity_id)

        # Cypher: 2-hop 관계와 주입했던 줄거리(chunk_summary)를 함께 가져옴
        cypher_query = """
        MATCH (e)
        WHERE toLower(e.id) = toLower($entity_id) OR toLower(e.name) = toLower($entity_id)
        MATCH p = (e)-[r*1..2]-(neighbor)
        WITH p, relationships(p) AS rels
        UNWIND rels AS rel
        RETURN 
            startNode(rel).id AS source, 
            type(rel) AS rel_type, 
            endNode(rel).id AS target,
            coalesce(endNode(rel).chunk_summary, "요약 정보 없음") AS plot_context,
            coalesce(endNode(rel).description, "") AS target_desc
        LIMIT 20
        """
        results = graph.query(cypher_query, params={"entity_id": entity_id})

        for row in results:
            # 관계 정보와 해당 장면의 줄거리를 결합하여 풍부한 문맥 생성
            context_line = f"({row['source']})-[:{row['rel_type']}]->({row['target']})"
            if row['plot_context'] != "요약 정보 없음":
                context_line += f" | 배경 줄거리: {row['plot_context']}"
            all_relationships.append(context_line)
    print("\n".join(list(set(all_relationships))))
    return "\n".join(list(set(all_relationships)))


# 4. 스마트 리트리버 통합
def smart_novel_retriever(question):
    # 질문에서 키워드 추출
    extracted = entity_extractor.invoke(f"다음 질문에서 소설 분석을 위한 핵심 엔티티를 추출하세요: {question}")

    contexts = []
    for name in extracted.names:
        # 하이브리드 검색 수행
        search_res = hybrid_retriever.invoke(name)
        # 그래프 경로 및 줄거리 추출
        contexts.append(get_enhanced_context(search_res))

    return "\n".join(contexts)


# 4. 소설 전용 RAG 체인 구성
template = """당신은 문학 평론가이자 소설 분석가입니다. 
제공된 '지식 그래프 컨텍스트'에 나타난 인물 관계, 사건의 흐름, 인물의 동기를 바탕으로 질문에 답하세요.

지식 그래프 컨텍스트:
{context}

질문: {question}

답변 (컨텍스트에 없는 내용은 소설 원문의 흐름을 추측하지 말고 모른다고 답하세요.):"""

prompt = ChatPromptTemplate.from_template(template)
chain = (
        {"context": smart_novel_retriever, "question": RunnablePassthrough()}
        | prompt | llm | StrOutputParser()
)

# 실행 예시
print(chain.invoke("주어진 컨텍스트에 대해 설명해줘"))