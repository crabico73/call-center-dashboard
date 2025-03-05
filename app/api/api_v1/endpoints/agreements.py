from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.db.session import get_db
from app.services.email_service import EmailService
from app.templates.service_agreement import generate_service_agreement
from app.models import models
from app.schemas import agreement as agreement_schemas
from datetime import datetime

router = APIRouter()
email_service = EmailService()

@router.post("/generate")
async def generate_agreement(
    agreement_data: agreement_schemas.AgreementCreate,
    db: Session = Depends(get_db)
):
    """Generate a service agreement based on call conversation"""
    # Get company information
    company = db.query(models.Company).filter(models.Company.id == agreement_data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get the latest call data
    call = db.query(models.Call).filter(
        models.Call.company_id == company.id
    ).order_by(models.Call.created_at.desc()).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="No call record found")
    
    # Prepare agreement data
    company_info = {
        "name": company.name,
        "address": agreement_data.company_address,
        "size": agreement_data.company_size,
        "requirements": agreement_data.requirements
    }
    
    call_metrics = {
        "monthly_volume": agreement_data.monthly_call_volume,
        "current_metrics": call.conversation_data
    }
    
    custom_terms = {
        "term_length": agreement_data.term_length,
        "additional_services": agreement_data.additional_services,
        "sla_requirements": agreement_data.sla_requirements,
        "payment_terms": agreement_data.payment_terms
    }
    
    # Generate agreement
    agreement_text = generate_service_agreement(
        company_info=company_info,
        call_metrics=call_metrics,
        custom_terms=custom_terms
    )
    
    # Create agreement record
    db_agreement = models.Agreement(
        company_id=company.id,
        content=agreement_text,
        status="pending_review",
        created_at=datetime.now()
    )
    db.add(db_agreement)
    db.commit()
    db.refresh(db_agreement)
    
    return {
        "agreement_id": db_agreement.id,
        "content": agreement_text,
        "status": "pending_review"
    }

@router.post("/{agreement_id}/submit")
async def submit_agreement(
    agreement_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit agreement for final review"""
    agreement = db.query(models.Agreement).filter(models.Agreement.id == agreement_id).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    company = db.query(models.Company).filter(models.Company.id == agreement.company_id).first()
    
    # Update agreement status
    agreement.status = "submitted"
    agreement.submitted_at = datetime.now()
    db.commit()
    
    # Send notification email for review
    background_tasks.add_task(
        email_service.send_agreement_notification,
        agreement_id=agreement.id,
        company_name=company.name,
        agreement_content=agreement.content
    )
    
    return {"status": "submitted", "message": "Agreement submitted for review"}

@router.post("/{agreement_id}/approve")
async def approve_agreement(
    agreement_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Approve and finalize the agreement"""
    agreement = db.query(models.Agreement).filter(models.Agreement.id == agreement_id).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    company = db.query(models.Company).filter(models.Company.id == agreement.company_id).first()
    
    # Update agreement status
    agreement.status = "approved"
    agreement.approved_at = datetime.now()
    db.commit()
    
    # Send confirmation emails
    background_tasks.add_task(
        email_service.send_agreement_confirmation,
        agreement_id=agreement.id,
        company_name=company.name,
        company_email=company.email
    )
    
    return {"status": "approved", "message": "Agreement has been approved and finalized"} 