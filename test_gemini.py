
import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print("Google API key loaded:", bool(api_key), flush=True)

if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is missing from .env")

try:
    print("Initializing Gemini model...", flush=True)

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
        timeout=30,
        max_retries=0,
        api_key=api_key,
    )

    print("Sending test request...", flush=True)
    start = time.time()

    response = llm.invoke(
        "Reply with only: Gemini test successful"
    )

    print(f"Response time: {time.time() - start:.2f} seconds", flush=True)
    print("SUCCESS:", response.content, flush=True)

except Exception as e:
    print("FAILED:", type(e).__name__, flush=True)
    print("Details:", str(e), flush=True)
