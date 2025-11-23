from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from .parser_engine import LogParserEngine
from datetime import datetime

router = APIRouter()
engine = LogParserEngine()

class LogRequest(BaseModel):
    content: str
    metadata: dict = {}

@router.post("/parse")
async def parse_log(request: Request, log_req: LogRequest):
    try:
        analysis = engine.parse(log_req.content)
        
        result_document = {
            "timestamp": datetime.utcnow(),
            "metadata": log_req.metadata,
            "analysis": analysis,
            "original_content_preview": log_req.content[:200]  # Store a preview
        }
        
        # Save to MongoDB
        if hasattr(request.app, 'database'):
            new_log = request.app.database["parsed_logs"].insert_one(result_document)
            result_document["_id"] = str(new_log.inserted_id)
        
        return {
            "status": "success",
            "data": result_document
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
