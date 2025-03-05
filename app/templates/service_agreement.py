from typing import Dict, Any
from datetime import datetime

SERVICE_AGREEMENT_TEMPLATE = """
AI SALES SOLUTIONS SERVICE AGREEMENT

This Service Agreement (the "Agreement") is entered into on {date} between:

AI Sales Solutions ("Provider")
and
{company_name} ("Client")
{company_address}

1. SERVICES
Provider will deliver AI-powered sales call services including:
- {num_calls} outbound calls per month
- AI agent configuration and training
- Real-time call analytics and reporting
- {custom_features}

2. PRICING AND TERMS
2.1 Base Package:
- Monthly Fee: ${base_price}
- Initial Term: {term_length} months
- Per-call rate beyond package limit: ${per_call_rate}

2.2 Additional Services:
{additional_services}

3. PERFORMANCE METRICS
Provider commits to maintaining:
- Minimum {success_rate}% successful connection rate
- Average call quality score of {quality_score}/10
- {custom_sla}

4. IMPLEMENTATION
- Setup Period: {setup_period} days
- Training Data Integration: {training_period} days
- Go-Live Date: {go_live_date}

5. PAYMENT TERMS
- Setup Fee: ${setup_fee} (one-time)
- Monthly Fee: ${monthly_fee}
- Payment Due: Net {payment_terms} days
- {custom_payment_terms}

6. TERMINATION
Either party may terminate this agreement with {termination_notice} days written notice after the initial term.

7. APPROVAL
This agreement requires final review and approval from an authorized AI Sales Solutions representative.

Client Signature: _____________________
Date: _____________________

AI Sales Solutions Review: _____________________
Date: _____________________
"""

def generate_service_agreement(
    company_info: Dict[str, Any],
    call_metrics: Dict[str, Any],
    custom_terms: Dict[str, Any]
) -> str:
    """
    Generates a customized service agreement based on the conversation and company needs.
    """
    # Calculate pricing based on volume and requirements
    base_price = calculate_base_price(call_metrics["monthly_volume"])
    
    # Format custom features based on conversation
    custom_features = format_custom_features(company_info["requirements"])
    
    # Generate agreement with all parameters
    agreement = SERVICE_AGREEMENT_TEMPLATE.format(
        date=datetime.now().strftime("%Y-%m-%d"),
        company_name=company_info["name"],
        company_address=company_info["address"],
        num_calls=call_metrics["monthly_volume"],
        custom_features=custom_features,
        base_price=base_price,
        term_length=custom_terms.get("term_length", 12),
        per_call_rate=calculate_per_call_rate(call_metrics["monthly_volume"]),
        additional_services=format_additional_services(custom_terms.get("additional_services", [])),
        success_rate=95,
        quality_score=8.5,
        custom_sla=format_custom_sla(custom_terms.get("sla_requirements", [])),
        setup_period=14,
        training_period=7,
        go_live_date=(datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
        setup_fee=calculate_setup_fee(company_info["size"]),
        monthly_fee=base_price,
        payment_terms=30,
        custom_payment_terms=format_payment_terms(custom_terms.get("payment_terms", {})),
        termination_notice=60
    )
    
    return agreement

def calculate_base_price(monthly_volume: int) -> float:
    """Calculate base price based on call volume"""
    base_rate = 0.50  # Base rate per call
    volume_discount = get_volume_discount(monthly_volume)
    return monthly_volume * base_rate * (1 - volume_discount)

def calculate_per_call_rate(monthly_volume: int) -> float:
    """Calculate per-call rate for calls beyond package limit"""
    base_rate = 0.50
    volume_discount = get_volume_discount(monthly_volume)
    return base_rate * (1 - volume_discount) * 1.2  # 20% premium for over-package calls

def get_volume_discount(monthly_volume: int) -> float:
    """Calculate volume discount percentage"""
    if monthly_volume > 10000:
        return 0.30
    elif monthly_volume > 5000:
        return 0.20
    elif monthly_volume > 1000:
        return 0.10
    return 0.0

def calculate_setup_fee(company_size: str) -> float:
    """Calculate one-time setup fee based on company size"""
    setup_fees = {
        "small": 1000,
        "medium": 2500,
        "large": 5000,
        "enterprise": 10000
    }
    return setup_fees.get(company_size.lower(), 2500)

def format_custom_features(requirements: List[str]) -> str:
    """Format custom features as bullet points"""
    return "\n".join([f"- {req}" for req in requirements])

def format_additional_services(services: List[Dict[str, Any]]) -> str:
    """Format additional services with pricing"""
    if not services:
        return "No additional services selected."
    
    return "\n".join([
        f"- {service['name']}: ${service['price']}/month"
        for service in services
    ])

def format_custom_sla(sla_requirements: List[str]) -> str:
    """Format custom SLA requirements"""
    if not sla_requirements:
        return "Standard SLA terms apply"
    
    return "\n".join([f"- {req}" for req in sla_requirements])

def format_payment_terms(terms: Dict[str, Any]) -> str:
    """Format custom payment terms"""
    if not terms:
        return "Standard payment terms apply"
    
    return "\n".join([f"- {k}: {v}" for k, v in terms.items()]) 