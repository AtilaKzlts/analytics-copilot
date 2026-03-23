from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / ".env")

@tool
def insight_tool(data: str) -> str:
    """
    SQL sonucu veya anomali tespiti sonucunu alır,
    iş dünyası perspektifinden yorumlar ve öneri üretir.
    """

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)

    prompt = ChatPromptTemplate.from_template("""
Sen deneyimli bir B2B satış analistisin. 
Aşağıdaki veri analizi sonucunu iş dünyası perspektifinden yorumla.

VERİ:
{data}

YAPMAN GEREKENLER:
- Sonucu sade İngilizce  ile açıkla
- Bu verinin iş için ne anlama geldiğini söyle
- 2-3 somut öneri sun
- Teknik jargon kullanma, satış müdürüne anlatır gibi anlat
- Gerçekten yapılabilir öneri yada eleştiri yap
- Çok uzun yapma okumas kolay olsun ancak çok kolaya da kaçma

YORUM:
""")

    chain = prompt | llm
    response = chain.invoke({"data": data})
    return response.content