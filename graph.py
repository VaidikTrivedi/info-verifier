import os
from dotenv import load_dotenv
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from schemas import AtomicClaim, VerifiedClaim, FinalReport, ContentAnalysis

load_dotenv()

# --- CONFIGURATION ---
# Set your free Gemini Key here or in your terminal: export GOOGLE_API_KEY="..."
if not os.environ.get("GEMINI_API_KEY"):
    raise EnvironmentError("Gemini API key not found")

# 1. Setup Gemini (Free)
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", # Flash is fast and free
    temperature=0,
    convert_system_message_to_human=True # specific tweak for Gemini
)

# 2. Setup DuckDuckGo (Free Search)
search_tool = DuckDuckGoSearchRun()

# --- THE STATE ---
class TribunalState(TypedDict):
    input_text: str
    claims: List[AtomicClaim]
    verified_claims: List[VerifiedClaim]
    final_report: FinalReport

# --- THE NODES ---

def decomposer_agent(state: TribunalState):
    print(f"--- [1/3] Decomposing: {state['input_text'][:50]}... ---")
    
    # Simple structured output prompt for Gemini
    structured_llm = llm.with_structured_output(ContentAnalysis)
    
    prompt = ChatPromptTemplate.from_messages([
        ("human", """Analyze this text. 
        1. Check if it is Satire/Fiction. 
        2. If NOT Satire, extract atomic claims.
        Text: {text}""")
    ])
    
    chain = prompt | structured_llm
    try:
        analysis = chain.invoke({"text": state["input_text"]})
        if analysis.is_satire_or_fiction: # type: ignore
            print("   -> Detected Satire. Skipping.")
            return {"claims": []}
        print(f"   -> Extracted {len(analysis.claims)} claims.") # type: ignore
        return {"claims": analysis.claims} # type: ignore
    except Exception as e:
        print(f"LLM Error: {e}")
        return {"claims": []}

def investigator_agent(state: TribunalState):
    print("--- [2/3] Investigating Claims ---")
    claims = state.get("claims", [])
    if not claims:
        return {"verified_claims": []}

    verified_results = []
    
    for claim in claims:
        print(f"   -> Searching for: {claim.claim_text}")
        
        # Aggregate search results from DuckDuckGo
        evidence_text = ""
        try:
            # We use the first generated query
            query = claim.search_queries[0]
            search_result = search_tool.invoke(query)
            evidence_text = search_result
        except Exception as e:
            evidence_text = f"Search failed: {str(e)}"

        # Verify
        verify_prompt = ChatPromptTemplate.from_messages([
            ("human", """You are a Judge. Verify this claim based strictly on the evidence.
            Claim: {claim}
            Evidence: {evidence}
            
            Return a JSON with status (VERIFIED/DEBUNKED/UNCERTAIN), reasoning, and confidence score.""")
        ])
        
        verifier = verify_prompt | llm.with_structured_output(VerifiedClaim)
        result = verifier.invoke({"claim": claim.claim_text, "evidence": evidence_text})
        verified_results.append(result)

    return {"verified_claims": verified_results}

def judge_agent(state: TribunalState):
    print("--- [3/3] Adjudicating ---")
    claims = state.get("verified_claims", [])
    
    if not claims:
        return {"final_report": FinalReport(overall_integrity_score=0.0, summary="No claims verified or Satire detected.", claims=[])}

    verified_count = len([c for c in claims if c.status == "VERIFIED"])
    score = (verified_count / len(claims)) * 100 if claims else 0

    report = FinalReport(
        overall_integrity_score=score,
        summary=f"Analysis Complete. {verified_count}/{len(claims)} claims verified.",
        claims=claims
    )
    return {"final_report": report}

# --- GRAPH BUILD ---
workflow = StateGraph(TribunalState)
workflow.add_node("decomposer", decomposer_agent)
workflow.add_node("investigator", investigator_agent)
workflow.add_node("judge", judge_agent)

workflow.set_entry_point("decomposer")
workflow.add_edge("decomposer", "investigator")
workflow.add_edge("investigator", "judge")
workflow.add_edge("judge", END)

app_graph = workflow.compile()