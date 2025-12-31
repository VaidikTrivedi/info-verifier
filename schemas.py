from pydantic import BaseModel, Field
from typing import List, Literal

class AtomicClaim(BaseModel):
    claim_text: str = Field(..., description="A single, verifiable fact extracted from the text.")
    original_sentence: str = Field(..., description="The sentence from the source text.")
    search_queries: List[str] = Field(..., description="Queries to verify this specific claim.")

class VerifiedClaim(BaseModel):
    claim_text: str
    status: Literal["VERIFIED", "DEBUNKED", "UNCERTAIN"]
    reasoning: str = Field(..., description="Why is it true/false? Logical steps.")
    evidence_sources: List[str] = Field(..., description="URLs supporting the verdict.")
    confidence_score: float = Field(..., description="0.0 to 1.0 integrity score.")

class ContentAnalysis(BaseModel):
    is_satire_or_fiction: bool = Field(..., description="True if the text is likely satire, parody, or fiction.")
    claims: List[AtomicClaim] = Field(..., description="List of claims only if the text is NOT satire. If satire, leave empty.")

class FinalReport(BaseModel):
    overall_integrity_score: float
    summary: str
    claims: List[VerifiedClaim]