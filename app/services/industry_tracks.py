from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class IndustryTrack:
    name: str
    key_metrics: List[str]
    pain_points: List[str]
    value_props: List[str]
    compliance_requirements: List[str]
    conversation_hooks: List[str]
    success_metrics: Dict[str, str]

class IndustryTracksService:
    def __init__(self):
        self.industry_tracks = {
            "financial_services": IndustryTrack(
                name="Financial Services",
                key_metrics=[
                    "Compliance violation rate",
                    "Script adherence percentage",
                    "Customer verification time",
                    "First call resolution rate",
                    "Regulatory reporting accuracy"
                ],
                pain_points=[
                    "Strict compliance requirements",
                    "High agent turnover due to stress",
                    "Complex script requirements",
                    "Extensive training needs",
                    "Risk of human error in compliance"
                ],
                value_props=[
                    "100% script compliance",
                    "Perfect regulatory adherence",
                    "Automated compliance reporting",
                    "Zero compliance violations",
                    "Consistent customer experience"
                ],
                compliance_requirements=[
                    "FDIC regulations",
                    "SEC guidelines",
                    "FINRA requirements",
                    "Consumer protection laws",
                    "Data privacy regulations"
                ],
                conversation_hooks=[
                    "How do you currently ensure 100% compliance in every call?",
                    "What's your current compliance violation rate?",
                    "How much time do you spend on compliance training?",
                    "What's the cost of a single compliance violation?"
                ],
                success_metrics={
                    "compliance_rate": "100%",
                    "error_reduction": "100%",
                    "training_cost_reduction": "90%",
                    "regulatory_reporting": "Automated"
                }
            ),
            
            "healthcare": IndustryTrack(
                name="Healthcare",
                key_metrics=[
                    "HIPAA compliance rate",
                    "Patient satisfaction scores",
                    "Appointment set rate",
                    "Follow-up completion rate",
                    "Information accuracy"
                ],
                pain_points=[
                    "HIPAA compliance challenges",
                    "Patient data sensitivity",
                    "Complex scheduling requirements",
                    "High volume of follow-ups",
                    "Detailed record-keeping needs"
                ],
                value_props=[
                    "Perfect HIPAA compliance",
                    "Consistent patient communication",
                    "Automated follow-up management",
                    "Accurate record-keeping",
                    "Improved patient satisfaction"
                ],
                compliance_requirements=[
                    "HIPAA regulations",
                    "Patient privacy rules",
                    "Medical information handling",
                    "Record retention requirements",
                    "Consent management"
                ],
                conversation_hooks=[
                    "How do you maintain HIPAA compliance across all calls?",
                    "What's your current patient follow-up rate?",
                    "How do you handle sensitive patient information?",
                    "What's your appointment no-show rate?"
                ],
                success_metrics={
                    "hipaa_compliance": "100%",
                    "follow_up_rate": "100%",
                    "data_accuracy": "100%",
                    "patient_satisfaction": "95%+"
                }
            ),
            
            "real_estate": IndustryTrack(
                name="Real Estate",
                key_metrics=[
                    "Lead qualification rate",
                    "Appointment set rate",
                    "Follow-up persistence",
                    "Contact reach rate",
                    "Lead response time"
                ],
                pain_points=[
                    "Inconsistent follow-up",
                    "Missed opportunities",
                    "Time-zone management",
                    "Lead response delays",
                    "Schedule coordination"
                ],
                value_props=[
                    "24/7 lead response",
                    "Perfect follow-up execution",
                    "Consistent lead nurturing",
                    "Automated scheduling",
                    "Improved conversion rates"
                ],
                compliance_requirements=[
                    "Fair Housing Act compliance",
                    "RESPA guidelines",
                    "State licensing rules",
                    "Do-not-call compliance",
                    "Privacy regulations"
                ],
                conversation_hooks=[
                    "What's your average lead response time?",
                    "How many follow-up attempts per lead?",
                    "What's your current lead conversion rate?",
                    "How do you handle after-hours leads?"
                ],
                success_metrics={
                    "response_time": "< 1 minute",
                    "follow_up_completion": "100%",
                    "lead_contact_rate": "95%+",
                    "appointment_set_rate": "40%+"
                }
            ),
            
            "technology": IndustryTrack(
                name="Technology",
                key_metrics=[
                    "Demo scheduling rate",
                    "Technical qualification accuracy",
                    "Lead scoring precision",
                    "Sales cycle length",
                    "Solution match rate"
                ],
                pain_points=[
                    "Complex product explanations",
                    "Technical knowledge requirements",
                    "Long sales cycles",
                    "Integration discussions",
                    "Feature comparison complexity"
                ],
                value_props=[
                    "Consistent technical accuracy",
                    "24/7 global coverage",
                    "Perfect product knowledge",
                    "Automated demo scheduling",
                    "Intelligent lead scoring"
                ],
                compliance_requirements=[
                    "Data protection regulations",
                    "Industry certifications",
                    "Security standards",
                    "Privacy requirements",
                    "International compliance"
                ],
                conversation_hooks=[
                    "How do you maintain technical accuracy across calls?",
                    "What's your current demo show-up rate?",
                    "How do you handle global time zones?",
                    "What's your technical qualification accuracy?"
                ],
                success_metrics={
                    "technical_accuracy": "100%",
                    "demo_schedule_rate": "50%+",
                    "qualification_precision": "95%+",
                    "global_coverage": "24/7"
                }
            )
        }
    
    def get_industry_track(self, industry: str) -> IndustryTrack:
        """Get the specific industry track configuration"""
        return self.industry_tracks.get(industry.lower())
    
    def get_industry_specific_roi_factors(self, industry: str) -> Dict[str, float]:
        """Get industry-specific ROI multipliers and factors"""
        industry_factors = {
            "financial_services": {
                "compliance_savings": 0.15,  # 15% additional savings from reduced compliance costs
                "risk_reduction_value": 0.10,  # 10% value add from reduced risk
                "training_savings": 0.20  # 20% additional savings on training
            },
            "healthcare": {
                "hipaa_compliance_value": 0.20,
                "patient_satisfaction_boost": 0.10,
                "record_keeping_savings": 0.15
            },
            "real_estate": {
                "lead_response_value": 0.25,
                "follow_up_efficiency": 0.15,
                "scheduling_optimization": 0.10
            },
            "technology": {
                "technical_accuracy_value": 0.15,
                "global_coverage_value": 0.20,
                "demo_efficiency_boost": 0.10
            }
        }
        return industry_factors.get(industry.lower(), {}) 