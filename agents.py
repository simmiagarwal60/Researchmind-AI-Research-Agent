
import os
from dotenv import load_dotenv

import streamlit as st
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_url

load_dotenv()


def get_google_api_key():
    # Local development: read the .env file or environment.
    api_key = os.getenv("GOOGLE_API_KEY")

    # Streamlit Cloud: read the configured app secret if needed.
    if not api_key:
        try:
            api_key = st.secrets.get("GOOGLE_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        raise RuntimeError(
            "Google API key not found. Set GOOGLE_API_KEY "
            "in your local .env file or Streamlit Cloud Secrets."
        )

    return api_key


# Shared Gemini model for all four stages.
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0,
    api_key=get_google_api_key(),
)


# Step 1: Search agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
    )


# Step 2: Reader / scraping agent
def build_scrape_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
    )


# Step 3: Writer chain
writer_prompt = ChatPromptTemplate([
    (
        "system",
        "You are an expert research writer. "
        "Write clear, structured and insightful reports."
    ),
    (
        "human",
        """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""
    ),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# Step 4: Critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp and constructive research critic. "
        "Be honest and specific."
    ),
    (
        "human",
        """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()
