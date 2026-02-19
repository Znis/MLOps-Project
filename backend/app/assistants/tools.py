from pydantic import BaseModel, Field
from app.vector_db import search_vector_db
from app.embeddings import get_embedding

class QueryKnowledgeBaseTool(BaseModel):
    """Search the document knowledge base to retrieve relevant passages. ALWAYS use this tool when the user asks ANY question about document content, facts, summaries, or information from indexed documents. Extract key search terms from the user's question and use them as the query_input. Examples: "machine learning", "financial summary", "project timeline", "key findings"."""
    query_input: str = Field(
        description='A clear, concise search query extracted from the user\'s question. Use 2-5 key words or a short phrase. Examples: "machine learning applications", "Q4 financial results", "project milestones", "safety protocols". Do NOT include question words like "what", "how", "why" - just the search terms.'
    )

    async def __call__(self, vector_db):
        query_vector = await get_embedding(self.query_input)
        chunks = await search_vector_db(query_vector, client=vector_db)
        formatted_sources = [f"SOURCE: {c['doc_name']}\n\"\"\"\n{c['text']}\n\"\"\"" for c in chunks]
        return "\n\n---\n\n".join(formatted_sources) + "\n\n---"
