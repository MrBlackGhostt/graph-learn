from mem0 import Memory, MemoryClient
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

key = "AIzaSyDi1WAG-CbMRONa2TnaFL2XWIe_xhvAquM"
if not key:
    raise ValueError("API key not found in environment variables.")

# First, read the PDF file content
with open("../srimad-bhagavata-mahapurana-english-translations.pdf", "rb") as file:
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
        "config": {"model": "models/embedding-001", "api_key": key},
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


pdf_url = "../srimad-bhagavata-mahapurana-english-translations.pdf"


system_prompt = """
You are a expert and guider for the user query form the story which answer in simple and detail answer
"""
pdf_message = {
    "role": "user",
    "content": {"type": "pdf_url", "pdf_url": {"url": pdf_url}},
}
# messages = [{"role": "user", "content": f"pdf_url: {pdf_url}"}]
mem_client.add([pdf_message], user_id="2")

# mem_client.add(
#     messages={"role": "user", "content": {"type": "pdf_url", "url": pdf_url}},
#     user_id="1",
# )


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
