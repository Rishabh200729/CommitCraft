import os
import sys
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

class TestOutput(BaseModel):
    summary: str = Field(description="A short summary")

async def main():
    print("Testing ChatGoogleGenerativeAI...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0
        )
        structured_llm = llm.with_structured_output(TestOutput)
        res = await structured_llm.ainvoke("Write a short summary about GitScribe.")
        print("Success:", res)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
