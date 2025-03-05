from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    industry = Column(String)
    status = Column(String)  # e.g., 'pending', 'contacted', 'qualified', 'not_interested'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    calls = relationship("Call", back_populates="company")
    contacts = relationship("Contact", back_populates="company")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String)
    position = Column(String)
    phone = Column(String)
    email = Column(String)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="contacts")
    calls = relationship("Call", back_populates="contact")

class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    agent_id = Column(String)  # AI agent identifier
    call_sid = Column(String)  # Twilio call SID
    status = Column(String)  # e.g., 'scheduled', 'in_progress', 'completed', 'failed'
    duration = Column(Integer)  # in seconds
    recording_url = Column(String)
    transcript = Column(Text)
    sentiment_score = Column(Float)
    conversation_data = Column(JSON)  # Store structured conversation data
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="calls")
    contact = relationship("Contact", back_populates="calls")

class AIAgent(Base):
    __tablename__ = "ai_agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    personality = Column(JSON)  # Store personality traits and behavior parameters
    prompt_template = Column(Text)  # Base prompt template for the agent
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 