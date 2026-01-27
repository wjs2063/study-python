from langchain_core.prompts import PromptTemplate
from langchain.agents.middleware import PIIMiddleware
from langgraph.store.memory import InMemoryStore

prompt = PromptTemplate(template="hi") + PromptTemplate(template="hello")

print(prompt)