"""
API Endpoints - Database-backed version
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from collections import defaultdict
from datetime import datetime, timedelta
import json
from app.models.db_models import Document, ChatHistory

from app.core.database import get_db
from app.models.schemas import (
    ChatRequest, UploadResponse, ProcessResponse, ReportResponse,
    QuickFacts, Statistics, Issue, AnalysisReport
)
from app.models.db_models import DocumentStatus
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.document_service import document_service
from app.services.analysis_service import analysis_service
from app.services.chat_service import chat_service
from app.core.config import settings

router = APIRouter()

# Rate limiting (still in-memory for simplicity, consider Redis for production)
user_requests = defaultdict(list)

@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):

    """Chat endpoint with RAG-enhanced responses"""
    print("CHAT REQUEST RAW:", req)
    print("USER ID:", req.user_id, type(req.user_id))

    
    # Rate limiting
    user_id = req.user_id or 0
    now = datetime.now()
    
    user_requests[user_id] = [
        req_time for req_time in user_requests[user_id]
        if now - req_time < timedelta(seconds=settings.RATE_LIMIT_SECONDS)
    ]
    
    if len(user_requests[user_id]) >= 1:
        time_to_wait = settings.RATE_LIMIT_SECONDS - (now - user_requests[user_id][0]).seconds
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {time_to_wait} seconds before asking another question."
        )
    
    user_requests[user_id].append(now)
    
    # Get latest document from database FOR THIS USER
    latest_doc = db.query(Document)\
        .filter(Document.user_id == user_id)\
        .filter(Document.status == DocumentStatus.COMPLETED)\
        .order_by(Document.created_at.desc())\
        .first()
    
    if not latest_doc:
        response = llm_service.chat(
            prompt=req.prompt,
            context={
                "contract_excerpt": "",
                "legal_context": "",
                "state": "NSW",
                "no_document": True
            }
        )
        return {"response": response}
    
    # DEBUG: Check document text
    print(f"\n🔍 CHAT DEBUG:")
    print(f"   Document ID: {latest_doc.id}")
    print(f"   Text exists: {latest_doc.text is not None}")
    print(f"   Text length: {len(latest_doc.text) if latest_doc.text else 0}")
    if latest_doc.text:
        print(f"   First 200 chars: {latest_doc.text[:200]}")
    else:
        print(f"   ⚠️ NO TEXT IN DOCUMENT!")
    
    # Get analysis
    analysis_record = analysis_service.get_analysis(db, latest_doc.id)
    clauses = analysis_record.clauses
    
    # Get legal context from RAG
    legal_context = rag_service.format_legal_context(
        req.prompt,
        latest_doc.state,
        n_results=3
    )
    
    # Build context for LLM
    context = {
        "contract_excerpt": latest_doc.text[:5000] if latest_doc.text else "",
        "legal_context": legal_context,
        "state": latest_doc.state,
        "filename": latest_doc.filename,
        "num_clauses": analysis_record.total_clauses,
        "high_risk": analysis_record.high_risk_clauses,
        "medium_risk": analysis_record.medium_risk_clauses,
        "illegal": analysis_record.illegal_clauses
    }
    
    # Get response
    try:
        response = llm_service.chat(req.prompt, context)
        
        # Save chat history
        chat_service.save_chat(
            db=db,
            document_id=latest_doc.id,
            user_id=user_id,
            prompt=req.prompt,
            response=response,
            state=latest_doc.state,
            laws_retrieved=len(legal_context) if legal_context else 0
        )
        
        return {"response": response}
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            raise HTTPException(
                status_code=429,
                detail="API quota exceeded. Please wait a minute and try again."
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    state: str = Query("NSW"),
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Upload and store document"""
    try:
        print(f"\n{'='*60}")
        print(f"🔍 UPLOAD DEBUG - Starting upload")
        print(f"   File: {file.filename}")
        print(f"   State: {state}")
        print(f"   User ID: {user_id}")
        
        # Extract text
        text = await document_service.extract_text_from_file(file)
        
        print(f"\n✅ TEXT EXTRACTED:")
        print(f"   Length: {len(text)} characters")
        print(f"   First 300 chars:\n   {text[:300]}")
        
        # Create document in database
        document = document_service.create_document(db, file.filename, text, state, user_id)
        
        print(f"\n✅ DOCUMENT CREATED:")
        print(f"   ID: {document.id}")
        print(f"   User ID: {document.user_id}")
        print(f"   Text length in object: {len(document.text) if document.text else 0}")
        
        # Verify by fetching back from DB
        verification = db.query(Document).filter(Document.id == document.id).first()
        
        print(f"\n✅ VERIFICATION (fetched from DB):")
        print(f"   Text exists: {verification.text is not None}")
        print(f"   Text length: {len(verification.text) if verification.text else 0}")
        print(f"   First 200 chars: {verification.text[:200] if verification.text else 'NO TEXT'}")
        print(f"{'='*60}\n")
        
        return UploadResponse(
            success=True,
            doc_id=document.id,
            filename=document.filename,
            state=document.state,
            detected_state=document.detected_state
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/process/{doc_id}", response_model=ProcessResponse)
async def process_document(doc_id: str, db: Session = Depends(get_db)):
    """Process and analyze document"""
    document = document_service.get_document(db, doc_id)
    
    print(f"\n📊 PROCESSING DOCUMENT:")
    print(f"   ID: {doc_id}")
    print(f"   Text length: {len(document.text) if document.text else 0}")
    
    try:
        # Update status to processing
        document_service.update_status(db, doc_id, DocumentStatus.PROCESSING)
        
        # Analyze with LLM
        result = llm_service.analyze_contract(document.text)
        
        # Save analysis to database
        analysis_service.create_analysis(db, doc_id, result)
        
        # Update status to completed
        document_service.update_status(db, doc_id, DocumentStatus.COMPLETED)
        
        return ProcessResponse(
            success=True,
            doc_id=doc_id,
            status="completed"
        )
    
    except Exception as e:
        document_service.set_error(db, doc_id, str(e))
        
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            raise HTTPException(
                status_code=429,
                detail="API quota exceeded. Please try again in a minute."
            )
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/report/{doc_id}")
async def get_report(doc_id: str, db: Session = Depends(get_db)):
    """Get analysis report"""
    document = document_service.get_document(db, doc_id)
    
    if document.status == DocumentStatus.UPLOADED or document.status == DocumentStatus.PROCESSING:
        return {"status": "processing", "message": "Analyzing..."}
    
    if document.status == DocumentStatus.ERROR:
        raise HTTPException(status_code=500, detail=document.error_message or "Unknown error")
    
    # Get analysis
    analysis = analysis_service.get_analysis(db, doc_id)
    
    # JSONB returns list directly, no need to parse
    clauses = analysis.clauses if analysis.clauses else []
    
    # Ensure clauses is a list
    if not isinstance(clauses, list):
        clauses = []
    
    # Build issues list
    issues = []
    
    # Check for state mismatch
    if document.detected_state and document.detected_state != document.state:
        issues.append(Issue(
            type="State Mismatch",
            title=f"⚠️ Document is from {document.detected_state}",
            description=f"This document appears to be a {document.detected_state} agreement, analyzed using {document.state} laws.",
            severity="MEDIUM",
            why_its_a_problem="Different states have different laws. This may affect accuracy.",
            page_reference="Document header"
        ))
    
    # Add clause issues
    for clause in clauses:
        # Ensure clause is a dictionary
        if not isinstance(clause, dict):
            continue
            
        if clause.get("soft_risk") in ["high", "medium"] or clause.get("illegal"):
            issues.append(Issue(
                type=clause.get("type", "other").replace("_", " ").title(),
                title=f"Clause {clause.get('clause_id')}: {clause.get('type', 'Unknown')}",
                description=clause.get("summary", "")[:200],
                severity="HIGH" if clause.get("soft_risk") == "high" or clause.get("illegal") else "MEDIUM",
                why_its_a_problem=" ".join(clause.get("illegal_reasons", [])) if clause.get("illegal_reasons") else "This clause may not comply with tenancy laws.",
                page_reference=f"Clause {clause.get('clause_id')}"
            ))
    
    # Format amounts
    rent_amount = f"${analysis.rent_amount:.2f}" if analysis.rent_amount else "Not specified"
    bond_amount = f"${analysis.bond_amount:.2f}" if analysis.bond_amount else "Not specified"
    
    # Build response
    analysis_report = AnalysisReport(
        overall_verdict=f"Contract Analysis for {document.state}",
        recommendation=f"Found {len(issues)} potential issue(s). " + 
                      ("Review high-risk clauses carefully." if analysis.high_risk_clauses > 0 else "Most clauses appear compliant."),
        risk_level=analysis.risk_level.value.upper(),
        quick_facts=QuickFacts(
            rent=rent_amount,
            bond=bond_amount,
            state=document.state,
            detected_state=document.detected_state,
            pages_analyzed=0
        ),
        statistics=Statistics(
            total_clauses_reviewed=analysis.total_clauses,
            illegal_clauses=analysis.illegal_clauses,
            high_risk_clauses=analysis.high_risk_clauses,
            medium_risk_clauses=analysis.medium_risk_clauses
        ),
        issues_found=issues,
        suggested_questions=[
            "What does this document say about...?",
            "Explain the bond requirements",
            "Can the landlord increase rent?",
            "What are my rights?"
        ]
    )
    
    return ReportResponse(
        success=True,
        doc_id=doc_id,
        filename=document.filename,
        state=document.state,
        analysis=analysis_report,
        status="completed"
    )


@router.get("/history/{doc_id}")
async def get_chat_history(doc_id: str, db: Session = Depends(get_db)):
    """Get chat history for a document"""
    chats = chat_service.get_document_chats(db, doc_id)
    
    return {
        "success": True,
        "doc_id": doc_id,
        "chats": [
            {
                "id": chat.id,
                "prompt": chat.prompt,
                "response": chat.response,
                "created_at": chat.created_at.isoformat()
            }
            for chat in chats
        ]
    }
    

@router.get("/user/{user_id}/conversations")
async def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    """Get all conversations for a user"""
    from app.models.db_models import Document, ChatHistory
    
    try:
        # Get all documents for this user, ordered by most recent
        documents = db.query(Document)\
            .filter(Document.user_id == user_id)\
            .filter(Document.status == DocumentStatus.COMPLETED)\
            .order_by(Document.created_at.desc())\
            .all()
        
        conversations = []
        
        for doc in documents:
            # Get the last chat message for this document
            last_chat = db.query(ChatHistory)\
                .filter(ChatHistory.document_id == doc.id)\
                .order_by(ChatHistory.created_at.desc())\
                .first()
            
            # Count total messages
            message_count = db.query(ChatHistory)\
                .filter(ChatHistory.document_id == doc.id)\
                .count()
            
            conversations.append({
                "doc_id": doc.id,
                "filename": doc.filename,
                "last_message": last_chat.response if last_chat else "Analysis complete",
                "last_message_time": (last_chat.created_at if last_chat else doc.created_at).isoformat(),
                "message_count": message_count
            })
        
        return {
            "success": True,
            "conversations": conversations
        }
        
    except Exception as e:
        print(f"Error fetching conversations: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))