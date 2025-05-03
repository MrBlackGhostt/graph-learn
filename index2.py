from dotenv import load_dotenv
import os
import story  # Import your story module
from mem0 import Memory
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Make sure this is set in your .env file
OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)  # Keep this if you're using any OpenAI services

# Neo4j and Qdrant configuration
QUADRANT_HOST = "localhost"
NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "reform-william-center-vibrate-press-5829"

# Configure Gemini AI
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


# Memory configuration
config = {
    "embedder": {
        "provider": "google",  # Using Google's embeddings
        "api_key": OPENAI_API_KEY,
        "model": "gemini-embedding-exp-03-07",
    },
    "llm": {
        "provider": "google",  # Using Google's LLM
        "config": {"api_key": OPENAI_API_KEY, "model": "gemini-2.0-flash-lite"},
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

# Initialize Memory
m = Memory.from_config(config)

print("Memory system initialized")


def chat(message):
    print("Processing message...")
    try:
        # Search for relevant memories
        mem_result = m.search(query=message, user_id="1")
        print("Memory search completed")

        # Format memories
        memories = "\n".join([m["memory"] for m in mem_result.get("results", [])])

        messages.append(
            {"role": "assistant", "content": result.choices[0].message.content}
        )
        # Create conversation
        result = client.chat.completions.create(
            model="gemini-2.0-flash-lite", messages=messages
        )

        messages = [
            {"role": "system", "content": f"{story.prompt} + {mem_result}"},
            {"role": "user", "content": message},
        ]

        result = client.chat.completions.create(
            model="gemini-2.0-flash-lite", messages=messages
        )

        # Store the conversation in memory
        messages.append(
            {"role": "assistant", "content": result.choices[0].message.content}
        )
        m.add(messages, user_id="1")

        return result.choices[0].message.content

    except Exception as e:
        print(f"Error in chat function: {e}")
        return f"I encountered an error: {str(e)}"


# Main loop
if __name__ == "__main__":
    print("Chat system ready. Type your messages (or 'exit' to quit):")
    while True:
        message = input(">> ")
        if message.lower() in ["exit", "quit"]:
            break
        print("Bot:", chat(message=message))
