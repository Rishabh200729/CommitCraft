import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .state import PRReviewState, CriticFileOutput

def critic_node(state: PRReviewState) -> dict:
    """
    Analyzes the raw PR diff for localized issues, file by file.
    Extracts security concerns, logic flaws, and code smells without knowing the broader architecture.
    """
    llm = ChatOpenAI(
        model="openrouter/auto", # Or a specific model like "google/gemini-2.5-flash" via OpenRouter
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0
    )
    structured_llm = llm.with_structured_output(CriticFileOutput)
    
    prompt = PromptTemplate.from_template("""
    You are an expert code critic reviewing a file's diff from a pull request.
    Your job is to identify security concerns, logic flaws, code smells, and reliability risks in THIS FILE ONLY.
    If you find no issues in a category, return an empty list.
    Do not guess or assume context outside of the provided diff.
    
    File Path: {file_path}
    File Diff:
    {diff}
    """)
    
    chain = prompt | structured_llm
    
    changed_files = state.get("changed_files", [])
    critic_flaws = {}
    
    for file_info in changed_files:
        file_path = file_info.get("file", "")
        diff_block = file_info.get("block", "")
        if not file_path or not diff_block:
            continue
            
        try:
            result = chain.invoke({"file_path": file_path, "diff": diff_block})
            # Convert the Pydantic model to dict
            critic_flaws[file_path] = result.model_dump()
        except Exception as e:
            # Handle potential LLM errors for a specific file
            print(f"Error processing {file_path} in Critic: {e}")
            critic_flaws[file_path] = {
                "security_concerns": [],
                "logic_flaws": [],
                "code_smells": [],
                "reliability_risks": [f"Error during AI analysis: {str(e)}"]
            }
            
    return {"critic_flaws": critic_flaws}

