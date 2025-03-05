from typing import Dict, Any, List
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class SubscriptionTier:
    name: str
    max_calls: int
    price_per_month: Decimal
    setup_fee: Decimal
    features: List[str]

class CostAnalysisService:
    def __init__(self):
        # Average costs in call center industry
        self.avg_agent_salary = 35000  # Annual salary
        self.avg_benefits_multiplier = 1.3  # 30% for benefits
        self.avg_agent_calls_per_day = 60
        self.avg_working_days_per_month = 21
        self.avg_overhead_per_agent = 500  # Monthly overhead (workspace, equipment, etc.)
        self.avg_turnover_cost = 4000  # Cost per agent replacement
        self.avg_turnover_rate = 0.30  # 30% annual turnover
        
        # Define subscription tiers
        self.subscription_tiers = [
            SubscriptionTier(
                name="Starter",
                max_calls=1000,
                price_per_month=Decimal("450"),  # $0.45 per call
                setup_fee=Decimal("1000"),
                features=[
                    "AI-powered outbound calls",
                    "Basic analytics dashboard",
                    "Standard business hours support",
                    "Basic call scripts"
                ]
            ),
            SubscriptionTier(
                name="Professional",
                max_calls=5000,
                price_per_month=Decimal("2000"),  # $0.40 per call
                setup_fee=Decimal("2500"),
                features=[
                    "All Starter features",
                    "24/7 call availability",
                    "Advanced analytics and reporting",
                    "Custom call scripts",
                    "Priority support",
                    "Call recording and transcription"
                ]
            ),
            SubscriptionTier(
                name="Enterprise",
                max_calls=10000,
                price_per_month=Decimal("3500"),  # $0.35 per call
                setup_fee=Decimal("5000"),
                features=[
                    "All Professional features",
                    "Dedicated account manager",
                    "Custom AI agent personalities",
                    "API integration",
                    "Advanced customization options",
                    "SLA guarantees",
                    "Training and onboarding support"
                ]
            ),
            SubscriptionTier(
                name="Ultimate",
                max_calls=25000,
                price_per_month=Decimal("7500"),  # $0.30 per call
                setup_fee=Decimal("10000"),
                features=[
                    "All Enterprise features",
                    "Multi-language support",
                    "Custom integration development",
                    "Dedicated development team",
                    "White-label options",
                    "Custom analytics development",
                    "Executive quarterly reviews"
                ]
            )
        ]
    
    def analyze_current_costs(self, 
                            num_agents: int,
                            calls_per_month: int,
                            avg_agent_salary: float = None) -> Dict[str, Any]:
        """Calculate current call center costs"""
        # Use provided salary or default
        agent_salary = avg_agent_salary or self.avg_agent_salary
        
        # Monthly costs
        monthly_salary = (agent_salary * self.avg_benefits_multiplier) / 12
        monthly_overhead = self.avg_overhead_per_agent
        monthly_turnover = (self.avg_turnover_cost * self.avg_turnover_rate) / 12
        
        total_monthly_cost = num_agents * (monthly_salary + monthly_overhead + monthly_turnover)
        cost_per_call = total_monthly_cost / calls_per_month if calls_per_month > 0 else 0
        
        return {
            "total_monthly_cost": round(total_monthly_cost, 2),
            "cost_per_call": round(cost_per_call, 2),
            "annual_cost": round(total_monthly_cost * 12, 2),
            "breakdown": {
                "salary_benefits": round(monthly_salary * num_agents, 2),
                "overhead": round(monthly_overhead * num_agents, 2),
                "turnover": round(monthly_turnover * num_agents, 2)
            }
        }
    
    def recommend_subscription(self, current_monthly_calls: int, current_monthly_cost: float) -> Dict[str, Any]:
        """Recommend the best subscription tier based on usage and cost"""
        target_monthly_cost = current_monthly_cost * 0.5  # Aim for 50% cost reduction
        
        # Find suitable tier based on call volume
        suitable_tiers = [
            tier for tier in self.subscription_tiers 
            if tier.max_calls >= current_monthly_calls
        ]
        
        if not suitable_tiers:
            return {
                "recommendation": "Custom Enterprise Solution",
                "message": "Your call volume exceeds our standard tiers. We'll create a custom solution.",
                "estimated_savings": None
            }
        
        # Get the most cost-effective tier
        recommended_tier = min(suitable_tiers, key=lambda x: x.price_per_month)
        
        monthly_savings = current_monthly_cost - float(recommended_tier.price_per_month)
        annual_savings = monthly_savings * 12
        roi_months = float(recommended_tier.setup_fee) / monthly_savings if monthly_savings > 0 else 0
        
        return {
            "recommendation": recommended_tier,
            "monthly_savings": round(monthly_savings, 2),
            "annual_savings": round(annual_savings, 2),
            "roi_months": round(roi_months, 1),
            "cost_reduction_percentage": round((monthly_savings / current_monthly_cost) * 100, 1)
        }
    
    def calculate_roi_metrics(self, 
                            current_costs: Dict[str, float],
                            selected_tier: SubscriptionTier) -> Dict[str, Any]:
        """Calculate detailed ROI metrics for the selected tier"""
        monthly_savings = current_costs["total_monthly_cost"] - float(selected_tier.price_per_month)
        annual_savings = monthly_savings * 12
        
        return {
            "monthly_savings": round(monthly_savings, 2),
            "annual_savings": round(annual_savings, 2),
            "setup_fee": float(selected_tier.setup_fee),
            "roi_metrics": {
                "payback_period_months": round(float(selected_tier.setup_fee) / monthly_savings, 1),
                "first_year_savings": round(annual_savings - float(selected_tier.setup_fee), 2),
                "five_year_savings": round((annual_savings * 5) - float(selected_tier.setup_fee), 2),
                "cost_reduction_percentage": round(
                    (monthly_savings / current_costs["total_monthly_cost"]) * 100, 1
                )
            },
            "operational_benefits": [
                "24/7 operation capability",
                "No turnover or training costs",
                "Consistent call quality",
                "Scalable capacity",
                "Real-time analytics and insights",
                "Zero HR management overhead"
            ]
        } 