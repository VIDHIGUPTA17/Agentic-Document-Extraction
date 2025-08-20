# Pydantic schemas for structured outputs
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class FieldExtract(BaseModel):
    name: str
    value: Optional[str]
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    source: Optional[Dict[str, Any]] = None  # e.g. {page:1, bbox:[x1,y1,x2,y2]}

class ExtractionResult(BaseModel):
    doc_type: str
    fields: List[FieldExtract]
    overall_confidence: float = Field(0.0, ge=0.0, le=1.0)
    qa: Optional[Dict[str, Any]] = None
