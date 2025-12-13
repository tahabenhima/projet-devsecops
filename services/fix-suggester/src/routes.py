from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from .database import get_db
from .models import FixSuggestion
from .fix_engine import FixEngine
from .diff_generator import generate_unified_diff, add_explanatory_comments

router = APIRouter()
fix_engine = FixEngine()

# Pydantic models for request/response
class VulnerabilityInput(BaseModel):
    type: str = Field(..., description="Type of vulnerability: unpinned_action, excessive_permissions, hardcoded_secret, weak_hardening")
    line: Optional[int] = Field(None, description="Line number where vulnerability was found")
    details: Optional[str] = Field(None, description="Additional details about the vulnerability")

class FixRequest(BaseModel):
    workflow_yaml: str = Field(..., description="GitHub Actions workflow YAML content")
    vulnerabilities: List[VulnerabilityInput] = Field(..., description="List of vulnerabilities to fix")

class FixResponse(BaseModel):
    id: int
    vulnerability_type: str
    description: str
    diff: str
    severity: str
    auto_applicable: bool

class FixesResponse(BaseModel):
    fixes: List[FixResponse]
    original_yaml: str
    fixed_yaml: str

@router.post("/fix", response_model=FixesResponse)
async def generate_fixes(request: FixRequest, db: Session = Depends(get_db)):
    """
    Generate fix suggestions for detected vulnerabilities.
    
    Args:
        request: Fix request with workflow YAML and vulnerabilities
        db: Database session
        
    Returns:
        Fix suggestions with diffs
    """
    try:
        fixes = []
        current_yaml = request.workflow_yaml
        
        for vulnerability in request.vulnerabilities:
            # Generate fix for this vulnerability
            fix_result = fix_engine.generate_fix(current_yaml, vulnerability.dict())
            fixed_yaml = fix_result['fixed_yaml']
            
            # Generate diff
            diff = generate_unified_diff(current_yaml, fixed_yaml)
            diff_with_comments = add_explanatory_comments(diff, vulnerability.type)
            
            # Save to database
            fix_suggestion = FixSuggestion(
                vulnerability_type=vulnerability.type,
                original_yaml=current_yaml,
                fixed_yaml=fixed_yaml,
                diff=diff_with_comments,
                description=fix_result['description'],
                severity=fix_result['severity'],
                auto_applicable=str(fix_result['auto_applicable']).lower()
            )
            db.add(fix_suggestion)
            db.commit()
            db.refresh(fix_suggestion)
            
            # Add to response
            fixes.append(FixResponse(
                id=fix_suggestion.id,
                vulnerability_type=fix_suggestion.vulnerability_type,
                description=fix_suggestion.description,
                diff=diff_with_comments,
                severity=fix_suggestion.severity,
                auto_applicable=fix_suggestion.auto_applicable == "true"
            ))
            
            # Update current YAML for next fix
            current_yaml = fixed_yaml
        
        return FixesResponse(
            fixes=fixes,
            original_yaml=request.workflow_yaml,
            fixed_yaml=current_yaml
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating fixes: {str(e)}")

@router.get("/fixes")
async def get_all_fixes(db: Session = Depends(get_db)):
    """
    Get all stored fix suggestions.
    
    Args:
        db: Database session
        
    Returns:
        List of all fix suggestions
    """
    fixes = db.query(FixSuggestion).all()
    return [
        {
            "id": fix.id,
            "vulnerability_type": fix.vulnerability_type,
            "description": fix.description,
            "severity": fix.severity,
            "timestamp": fix.timestamp.isoformat()
        }
        for fix in fixes
    ]

@router.get("/fixes/{fix_id}")
async def get_fix_by_id(fix_id: int, db: Session = Depends(get_db)):
    """
    Get a specific fix suggestion by ID.
    
    Args:
        fix_id: Fix suggestion ID
        db: Database session
        
    Returns:
        Fix suggestion details
    """
    fix = db.query(FixSuggestion).filter(FixSuggestion.id == fix_id).first()
    if not fix:
        raise HTTPException(status_code=404, detail="Fix suggestion not found")
    
    return {
        "id": fix.id,
        "vulnerability_type": fix.vulnerability_type,
        "description": fix.description,
        "original_yaml": fix.original_yaml,
        "fixed_yaml": fix.fixed_yaml,
        "diff": fix.diff,
        "severity": fix.severity,
        "auto_applicable": fix.auto_applicable == "true",
        "timestamp": fix.timestamp.isoformat()
    }
