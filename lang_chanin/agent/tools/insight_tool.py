from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / ".env")

@tool
def insight_tool(data: str) -> str:
    """
    Takes SQL results or anomaly detection output and generates
    a plain-language business interpretation with recommendations.
    """

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)

    prompt = ChatPromptTemplate.from_template("""
You are an experienced B2B sales analyst.
Interpret the following data analysis result from a business perspective.

DATA:
{data}

INSTRUCTIONS:
- Explain in clear, plain English
- Tell what this means for the business
- Give 2-3 concrete, actionable recommendations
- Write like you're briefing a sales director — no jargon
- Keep it concise but not superficial
- Be direct, not generic

ANALYSIS:
""")

    chain = prompt | llm
    response = chain.invoke({"data": data})
    return response.content