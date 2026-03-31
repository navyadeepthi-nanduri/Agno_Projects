from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

from pypdf import PdfReader
import lancedb
from sentence_transformers import SentenceTransformer
import os

# vLLM config
os.environ["OPENAI_BASE_URL"] = "http://vllm.dealwallet.com:8080/v1"
os.environ["OPENAI_API_KEY"] = "lIsJqsUPjkLE_BzQm48JDtKB_ubPeJd28adqWdNJgrE"

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Read PDF
reader = PdfReader("ThaiRecipes.pdf")
texts = []

for page in reader.pages:
    if page.extract_text():
        texts.append(page.extract_text())

# Create embeddings
vectors = embed_model.encode(texts)

# Store in LanceDB
db = lancedb.connect("lancedb")

table = db.create_table(
    "recipes",
    data=[{"text": t, "vector": v.tolist()} for t, v in zip(texts, vectors)],
    mode="overwrite"
)

# Search function
def search_pdf(query):
    qvec = embed_model.encode([query])[0]
    results = table.search(qvec).limit(3).to_list()
    return "\n".join([r["text"] for r in results])


# Agent
agent = Agent(
    model=OpenAIChat(
        id="Qwen/Qwen2.5-7B-Instruct"
    ),
    instructions=dedent("""
You are a Thai cuisine expert.
Use provided recipe knowledge when answering.
"""),
    tools=[DuckDuckGoTools()],
    markdown=True,
)

# Ask question
question = "How do I make Thai curry?"

pdf_info = search_pdf(question)

agent.print_response(
    f"Answer using this knowledge:\n{pdf_info}\n\nQuestion: {question}",
    stream=True,
)