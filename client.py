from dotenv import load_dotenv
from openai import OpenAI
import os
from openai import OpenAI
from mem0 import Memory
import text
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API key not found in environment variables.")


QUADRANT_HOST = "localhost"

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "reform-william-center-vibrate-press-5829"
config = {
    "embedder": {
        "provider": "gemini",
        "config": {"model": "models/embedding-001", "api_key": api_key},
        "embedding_dims": 768,
    },
    "llm": {
        "provider": "gemini",
        "config": {"api_key": api_key, "model": "gemini-2.0-flash-lite"},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QUADRANT_HOST,
            "port": 6333,
            "collection_name": "story",
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
    # "custom_fact_extraction_prompt": text.prompt,
    "version": "v1.1",
}


# Create the client of MemO

mem_client = Memory.from_config(config)

messages = [{"role": "user", "content": text.story}]


def chat(user_message):
    mem_result = mem_client.search(query=user_message, user_id="1")

    memories = "\n".join([m["memory"] for m in mem_result.get("results")])
    print(f"\n\nMEMORY:\n\n{memories}\n\n")

    messages.extend(
        [
            {"role": "system", "content": f"{text.prompt} + {memories}"},
            {"role": "user", "content": user_message},
        ]
    )

    result = client.chat.completions.create(
        model="gemini-2.0-flash-lite", messages=messages
    )

    messages.append({"role": "assistant", "content": result.choices[0].message.content})

    mem_client.add(messages=result.choices[0].message.content, user_id="1")

    return result.choices[0].message.content


client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

while True:
    query = input("Enter your query : ")
    res = chat(query)
    print("RESULT", res)
