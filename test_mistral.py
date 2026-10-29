import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()

print("API key loaded:", bool(os.getenv("MISTRAL_API_KEY")))

try:
    llm = ChatMistralAI(
        model="mistral-small-2603",
        temperature=0,
    )

    response = llm.invoke("Reply with only: API test successful")
    print("SUCCESS:", response.content)

except Exception as e:
    print("FAILED:", type(e).__name__)
    print(str(e))