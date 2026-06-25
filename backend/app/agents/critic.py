import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .state import PRReviewState, CriticOutput

def critic_node(state: PRReviewState) -> dict:
    """
    Analyzes the raw PR diff for localized issues.
    Extracts security concerns, logic flaws, and code smells without knowing the broader architecture.
    """
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        model="google/gemma-4-31b-it:free",
        temperature=0,
        extra_body={"reasoning": {"enabled": True}}
    )
    structured_llm = llm.with_structured_output(CriticOutput)
    
    prompt = PromptTemplate.from_template("""
    You are an expert code critic reviewing a pull request diff.
    Your job is to identify security concerns, logic flaws, code smells, and reliability risks.
    If you find no issues in a category, return an empty list.
    Do not guess or assume context outside of the diff.
    
    PR Diff:
    {diff}
    """)
    
    chain = prompt | structured_llm
    result = chain.invoke({"diff": state.get("pr_diff", "")})
    
    return {"critic_flaws": result.dict()}
