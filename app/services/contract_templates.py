from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class ComplianceRequirement:
    name: str
    description: str
    certification_needed: bool
    audit_frequency: int  # months
    reporting_requirements: List[str]

@dataclass
class ServiceLevel:
    name: str
    availability: float
    response_time: int  # minutes
    resolution_time: int  # hours
    penalties: Dict[str, float]

@dataclass
class ContractTerms:
    initial_term: int  # months
    auto_renewal_term: int  # months
    termination_notice: int  # days
    early_termination_fee: float  # percentage of remaining contract value
    payment_terms: int  # days
    price_increase_cap: float  # percentage

class ContractTemplateService:
    def __init__(self):
        # Industry-specific compliance requirements
        self.compliance_requirements = {
            "FINANCIAL": [
                ComplianceRequirement(
                    name="Data Security",
                    description="SOC 2 Type II compliance for data handling",
                    certification_needed=True,
                    audit_frequency=12,
                    reporting_requirements=[
                        "Monthly security reports",
                        "Incident response documentation",
                        "Access logs retention"
                    ]
                ),
                ComplianceRequirement(
                    name="Transaction Monitoring",
                    description="BSA/AML compliance monitoring",
                    certification_needed=True,
                    audit_frequency=6,
                    reporting_requirements=[
                        "Suspicious activity reports",
                        "Transaction monitoring logs",
                        "Compliance officer review"
                    ]
                )
            ],
            "HEALTHCARE": [
                ComplianceRequirement(
                    name="HIPAA Compliance",
                    description="Protected Health Information handling",
                    certification_needed=True,
                    audit_frequency=6,
                    reporting_requirements=[
                        "PHI access logs",
                        "Security incident reports",
                        "Patient data handling procedures"
                    ]
                ),
                ComplianceRequirement(
                    name="Data Privacy",
                    description="Patient data protection standards",
                    certification_needed=True,
                    audit_frequency=12,
                    reporting_requirements=[
                        "Privacy impact assessments",
                        "Data encryption verification",
                        "Access control documentation"
                    ]
                )
            ]
        }

        # Industry-specific SLAs
        self.service_levels = {
            "FINANCIAL": ServiceLevel(
                name="Financial Grade",
                availability=0.9999,  # 99.99% uptime
                response_time=5,      # 5 minutes
                resolution_time=2,    # 2 hours
                penalties={
                    "availability": 0.1,  # 10% credit for missing SLA
                    "response_time": 0.05,
                    "resolution_time": 0.05
                }
            ),
            "HEALTHCARE": ServiceLevel(
                name="Healthcare Grade",
                availability=0.999,   # 99.9% uptime
                response_time=15,     # 15 minutes
                resolution_time=4,    # 4 hours
                penalties={
                    "availability": 0.15,
                    "response_time": 0.07,
                    "resolution_time": 0.07
                }
            )
        }

        # Industry-specific contract terms
        self.default_terms = {
            "FINANCIAL": ContractTerms(
                initial_term=36,
                auto_renewal_term=12,
                termination_notice=90,
                early_termination_fee=0.75,
                payment_terms=30,
                price_increase_cap=0.05
            ),
            "HEALTHCARE": ContractTerms(
                initial_term=24,
                auto_renewal_term=12,
                termination_notice=60,
                early_termination_fee=0.50,
                payment_terms=45,
                price_increase_cap=0.07
            )
        }

    def generate_contract(self,
                         industry: str,
                         company_info: Dict[str, Any],
                         subscription_details: Dict[str, Any],
                         custom_terms: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate industry-specific contract"""
        
        # Get base templates
        compliance_reqs = self.compliance_requirements.get(
            industry.upper(),
            self.compliance_requirements["FINANCIAL"]  # Default to financial
        )
        
        service_level = self.service_levels.get(
            industry.upper(),
            self.service_levels["FINANCIAL"]  # Default to financial
        )
        
        terms = self.default_terms.get(
            industry.upper(),
            self.default_terms["FINANCIAL"]  # Default to financial
        )
        
        # Override with custom terms if provided
        if custom_terms:
            terms = self._merge_custom_terms(terms, custom_terms)
        
        # Calculate dates
        start_date = datetime.now() + timedelta(days=14)  # Default 2 weeks setup
        initial_term_end = start_date + timedelta(days=terms.initial_term * 30)
        
        contract = {
            "metadata": {
                "industry": industry,
                "generated_date": datetime.now().isoformat(),
                "version": "1.0"
            },
            "parties": {
                "provider": {
                    "name": "AI Sales Solutions",
                    "address": "Provider Address",
                    "contact": "Provider Contact"
                },
                "client": company_info
            },
            "terms": {
                "start_date": start_date.isoformat(),
                "initial_term_end": initial_term_end.isoformat(),
                "initial_term_months": terms.initial_term,
                "auto_renewal_term": terms.auto_renewal_term,
                "termination_notice_days": terms.termination_notice,
                "early_termination_fee": terms.early_termination_fee,
                "payment_terms_days": terms.payment_terms,
                "price_increase_cap": terms.price_increase_cap
            },
            "service_levels": {
                "availability": service_level.availability,
                "response_time_minutes": service_level.response_time,
                "resolution_time_hours": service_level.resolution_time,
                "penalties": service_level.penalties
            },
            "compliance": {
                requirement.name: {
                    "description": requirement.description,
                    "certification_needed": requirement.certification_needed,
                    "audit_frequency_months": requirement.audit_frequency,
                    "reporting_requirements": requirement.reporting_requirements
                }
                for requirement in compliance_reqs
            },
            "subscription": subscription_details,
            "usage_terms": self._generate_usage_terms(industry, subscription_details),
            "data_handling": self._generate_data_handling_terms(industry),
            "termination": self._generate_termination_terms(terms)
        }
        
        return contract

    def _merge_custom_terms(self,
                          base_terms: ContractTerms,
                          custom_terms: Dict[str, Any]) -> ContractTerms:
        """Merge custom terms with base terms"""
        return ContractTerms(
            initial_term=custom_terms.get("initial_term", base_terms.initial_term),
            auto_renewal_term=custom_terms.get("auto_renewal_term", base_terms.auto_renewal_term),
            termination_notice=custom_terms.get("termination_notice", base_terms.termination_notice),
            early_termination_fee=custom_terms.get("early_termination_fee", 
                                                 base_terms.early_termination_fee),
            payment_terms=custom_terms.get("payment_terms", base_terms.payment_terms),
            price_increase_cap=custom_terms.get("price_increase_cap", base_terms.price_increase_cap)
        )

    def _generate_usage_terms(self,
                            industry: str,
                            subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Generate industry-specific usage terms"""
        base_terms = {
            "authorized_use": [
                "Outbound sales calls",
                "Lead qualification",
                "Appointment setting",
                "Follow-up calls"
            ],
            "prohibited_use": [
                "Unauthorized data collection",
                "Competitive analysis",
                "System reverse engineering"
            ],
            "data_retention": "90 days",
            "usage_limits": {
                "max_calls_per_month": subscription.get("max_calls", 0),
                "max_concurrent_calls": subscription.get("max_concurrent", 10),
                "operating_hours": "24/7"
            }
        }
        
        # Add industry-specific terms
        if industry.upper() == "FINANCIAL":
            base_terms["authorized_use"].extend([
                "Regulatory compliance checks",
                "Transaction verification"
            ])
            base_terms["data_retention"] = "7 years"
        
        elif industry.upper() == "HEALTHCARE":
            base_terms["authorized_use"].extend([
                "Patient appointment scheduling",
                "Insurance verification"
            ])
            base_terms["prohibited_use"].append("PHI sharing")
            base_terms["data_retention"] = "6 years"
        
        return base_terms

    def _generate_data_handling_terms(self, industry: str) -> Dict[str, Any]:
        """Generate industry-specific data handling terms"""
        base_terms = {
            "data_classification": [
                "Public",
                "Internal",
                "Confidential"
            ],
            "security_measures": [
                "Encryption at rest",
                "Encryption in transit",
                "Access controls",
                "Audit logging"
            ],
            "backup_frequency": "Daily",
            "retention_period": "90 days"
        }
        
        if industry.upper() == "FINANCIAL":
            base_terms["data_classification"].append("Regulated")
            base_terms["security_measures"].extend([
                "Multi-factor authentication",
                "Real-time monitoring",
                "Fraud detection"
            ])
            base_terms["retention_period"] = "7 years"
        
        elif industry.upper() == "HEALTHCARE":
            base_terms["data_classification"].extend([
                "PHI",
                "Electronic Health Records"
            ])
            base_terms["security_measures"].extend([
                "HIPAA compliance",
                "PHI encryption",
                "Access tracking"
            ])
            base_terms["retention_period"] = "6 years"
        
        return base_terms

    def _generate_termination_terms(self, terms: ContractTerms) -> Dict[str, Any]:
        """Generate termination-related terms"""
        return {
            "notice_period_days": terms.termination_notice,
            "early_termination_fee": f"{terms.early_termination_fee * 100}% of remaining contract value",
            "data_handling_post_termination": {
                "data_retention_period": "30 days",
                "data_deletion_certificate": True,
                "transition_assistance": "60 days"
            },
            "renewal_terms": {
                "auto_renewal": True,
                "renewal_term_months": terms.auto_renewal_term,
                "renewal_notice_days": 60,
                "maximum_price_increase": f"{terms.price_increase_cap * 100}%"
            },
            "termination_triggers": [
                "Material breach",
                "Bankruptcy",
                "Force majeure",
                "Regulatory requirements"
            ]
        } 