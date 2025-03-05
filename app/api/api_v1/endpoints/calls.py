from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.services.ai_call_service import AICallService
from app.models import models
from app.schemas import call as call_schemas
import asyncio

router = APIRouter()
ai_call_service = AICallService()

@router.post("/initiate", response_model=call_schemas.CallCreate)
async def initiate_call(
    call_data: call_schemas.CallCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Initiate a new AI agent call"""
    # Get company and contact info
    company = db.query(models.Company).filter(models.Company.id == call_data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    contact = db.query(models.Contact).filter(models.Contact.id == call_data.contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Get AI agent configuration
    agent = db.query(models.AIAgent).filter(models.AIAgent.id == call_data.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="AI Agent not found")
    
    # Create call record
    db_call = models.Call(
        company_id=company.id,
        contact_id=contact.id,
        agent_id=agent.id,
        status="scheduled",
        scheduled_at=call_data.scheduled_at
    )
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    
    # Schedule the call
    background_tasks.add_task(
        ai_call_service.initiate_call,
        contact.phone,
        agent.personality
    )
    
    return db_call

@router.post("/webhook")
async def call_webhook(request_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Handle Twilio webhook for call events"""
    call_sid = request_data.get("CallSid")
    if not call_sid:
        raise HTTPException(status_code=400, detail="CallSid not provided")
    
    # Get call from database
    call = db.query(models.Call).filter(models.Call.call_sid == call_sid).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Handle the webhook event
    event_type = request_data.get("EventType")
    if event_type == "initiated":
        call.status = "in_progress"
        call.started_at = request_data.get("Timestamp")
    elif event_type == "completed":
        call.status = "completed"
        call.ended_at = request_data.get("Timestamp")
        call.duration = request_data.get("CallDuration")
    
    db.commit()
    
    return {"status": "success"}

@router.get("/{call_id}", response_model=call_schemas.Call)
async def get_call(call_id: int, db: Session = Depends(get_db)):
    """Get call details"""
    call = db.query(models.Call).filter(models.Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call

@router.get("/company/{company_id}", response_model=List[call_schemas.Call])
async def get_company_calls(company_id: int, db: Session = Depends(get_db)):
    """Get all calls for a company"""
    calls = db.query(models.Call).filter(models.Call.company_id == company_id).all()
    return calls 