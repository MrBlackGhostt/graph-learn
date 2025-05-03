import story
from dotenv import load_dotenv
import os
from openai import OpenAI
from mem0 import Memory

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

QUADRANT_HOST = "localhost"

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "reform-william-center-vibrate-press-5829"

config = {
    "embedder": {
        "api_key": api_key,
        "model": "gemini-embedding-exp-03-07",
    },
    "llm": {
        "provider": "openai",
        "config": {"api_key": api_key, "model": "gemini-2.0-flash-lite"},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QUADRANT_HOST,
            "port": 6333,
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
}

m = Memory.from_config(config)

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

print("AFTERT TEH CLIENT")


def chat(message):
    print(f"Inside the chat")
    mem_result = m.search(query=message, user_id="1")

    print("MEM RESULT", mem_result)

    memories = "\n".join([m["memory"] for m in mem_result.get("results")])
    # print(f"\n\nMEMORY:\n\n{memories}\n\n")

    messages = [
        {"role": "system", "content": f"{story.prompt} + {mem_result}"},
        {"role": "user", "content": message},
    ]

    result = client.chat.completions.create(
        model="gemini-2.0-flash-lite", messages=messages
    )

    messages.append({"role": "assistant", "content": result.choices[0].message.content})

    m.add(messages, user_id="1")

    return result.choices[0].message.content


while True:
    message = input(">> ")
    print("Bot: ", chat(message=message))
