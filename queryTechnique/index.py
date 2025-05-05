from mem0 import Memory, MemoryClient
import os
from dotenv import load_dotenv
from openai import OpenAI
import fitz
import time

load_dotenv()

key = ""
if not key:
    raise ValueError("API key not found in environment variables.")

pdf_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../srimad-bhagavata-mahapurana-english-translations.pdf",
    )
)

print("Resolved PDF path:", pdf_path)

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

doc = fitz.open(pdf_path)
pdf_text = "\n".join([page.get_text() for page in doc])

# First, read the PDF file content
with open(pdf_path, "rb") as file:
    pdf_content = file.read()

client = OpenAI(
    api_key=key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


QUADRANT_HOST = "localhost"

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "reform-william-center-vibrate-press-5829"
config = {
    "embedder": {
        "provider": "gemini",
        "config": {"model": "models/text-embedding-004", "api_key": key},
        "embedding_dims": 768,
    },
    "llm": {
        "provider": "gemini",
        "config": {"api_key": key, "model": "gemini-2.0-flash-lite"},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QUADRANT_HOST,
            "port": 6333,
            "collection_name": "bhagvita",
            "embedding_model_dims": 768,
        },
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URL,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD,
        },
    },
    "version": "v1.1",
}

mem_client = Memory.from_config(config)


def chunk_text(text, chunk_size=1000):
    words = text.split()
    return [
        " ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)
    ]


chunks = chunk_text(pdf_text)

for chunk in chunks:
    mem_client.add([{"role": "user", "content": chunk}], user_id="2")
    time.sleep(2)


# pdf_url = "../srimad-bhagavata-mahapurana-english-translations.pdf"


system_prompt = """
You are a expert and guider for the user query form the story which answer in simple and detail answer
"""


def chat(query):
    print(f"INSIDE CHAT")
    search = mem_client.search(query=query, user_id="2")
    memories = "\n".join([m["memory"] for m in search.get("results")])
    print(f"\n\nMEMORY:\n\n{memories}\n\n")
    print("MEMORIES", memories, "\n")

    messages = [
        {"role": "system", "content": system_prompt + memories},
        {"role": "user", "content": query},
    ]

    result = client.chat.completions.create(
        model="gemini-2.0-flash-lite", messages=messages
    )
    print("GOT THE REUSLT OF THE QUERY", result)
    messages.append({"role": "assistant", "content": result.choices[0].message.content})

    mem_client.add([messages[-1]], user_id="2")

    return result.choices[0].message.content


while True:
    query = input("enter the query : ")
    res = chat(query)
    print("Query completer")
    print("RESULT", res)
