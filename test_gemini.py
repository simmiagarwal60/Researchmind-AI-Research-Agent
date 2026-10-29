
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print("Google API key loaded:", bool(api_key))

if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is missing from .env")

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        temperature=0,
        api_key=api_key,
    )

    response = llm.invoke("Reply with only: Gemini test successful")
    print("SUCCESS:", response.content)

except Exception as e:
    print("FAILED:", type(e).__name__)
    print(str(e))
