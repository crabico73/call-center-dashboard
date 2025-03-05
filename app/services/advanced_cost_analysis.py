from typing import Dict, Any, List
from dataclasses import dataclass
from decimal import Decimal
import statistics

@dataclass
class CompetitorProfile:
    name: str
    avg_cost_per_call: float
    features: List[str]
    limitations: List[str]
    market_focus: str
    pricing_model: str

class AdvancedCostAnalysisService:
    def __init__(self):
        # Industry benchmarks
        self.industry_benchmarks = {
            "cost_per_call": {
                "low": 6.0,
                "average": 8.0,
                "high": 12.0
            },
            "agent_utilization": {
                "low": 0.65,
                "average": 0.75,
                "high": 0.85
            },
            "conversion_rates": {
                "low": 0.02,
                "average": 0.05,
                "high": 0.10
            }
        }
        
        # Competitor analysis
        self.competitors = {
            "traditional_call_center": CompetitorProfile(
                name="Traditional Call Center",
                avg_cost_per_call=8.0,
                features=[
                    "Human agents",
                    "Standard training",
                    "Basic reporting",
                    "Limited hours"
                ],
                limitations=[
                    "High turnover",
                    "Inconsistent quality",
                    "Limited scalability",
                    "Training requirements"
                ],
                market_focus="General",
                pricing_model="Per agent/hour"
            ),
            "cloud_contact": CompetitorProfile(
                name="Cloud Contact Solutions",
                avg_cost_per_call=6.5,
                features=[
                    "Cloud infrastructure",
                    "Basic automation",
                    "Standard reporting",
                    "Multiple channels"
                ],
                limitations=[
                    "Limited AI capabilities",
                    "Basic automation only",
                    "Generic solutions",
                    "Minimal customization"
                ],
                market_focus="Small Business",
                pricing_model="Per seat/month"
            ),
            "ai_assist": CompetitorProfile(
                name="AI Assistant Tools",
                avg_cost_per_call=5.0,
                features=[
                    "Basic AI support",
                    "Template responses",
                    "Simple automation",
                    "Standard hours"
                ],
                limitations=[
                    "Limited customization",
                    "Basic AI only",
                    "No full conversation handling",
                    "Limited integration"
                ],
                market_focus="Tech startups",
                pricing_model="Per user/month"
            )
        }

    def analyze_total_cost_of_ownership(self,
                                      num_agents: int,
                                      calls_per_month: int,
                                      avg_agent_salary: float,
                                      industry: str) -> Dict[str, Any]:
        """Detailed TCO analysis including hidden costs"""
        
        # Direct costs
        direct_costs = self._calculate_direct_costs(num_agents, avg_agent_salary)
        
        # Indirect costs
        indirect_costs = self._calculate_indirect_costs(num_agents, calls_per_month)
        
        # Opportunity costs
        opportunity_costs = self._calculate_opportunity_costs(num_agents, calls_per_month)
        
        # Industry-specific costs
        industry_costs = self._calculate_industry_specific_costs(industry, num_agents, calls_per_month)
        
        total_monthly_cost = sum([
            direct_costs["total"],
            indirect_costs["total"],
            opportunity_costs["total"],
            industry_costs["total"]
        ])
        
        return {
            "total_monthly_cost": round(total_monthly_cost, 2),
            "cost_per_call": round(total_monthly_cost / calls_per_month, 2),
            "breakdown": {
                "direct_costs": direct_costs,
                "indirect_costs": indirect_costs,
                "opportunity_costs": opportunity_costs,
                "industry_specific_costs": industry_costs
            },
            "benchmarks": self._get_benchmark_comparison(total_monthly_cost / calls_per_month),
            "competitive_analysis": self._get_competitive_analysis(total_monthly_cost / calls_per_month)
        }

    def _calculate_direct_costs(self, num_agents: int, avg_agent_salary: float) -> Dict[str, float]:
        """Calculate direct costs including salary, benefits, and infrastructure"""
        monthly_salary = (avg_agent_salary / 12)
        benefits = monthly_salary * 0.3
        equipment = 200  # Monthly equipment and software costs per agent
        infrastructure = 300  # Monthly infrastructure costs per agent
        
        total = num_agents * (monthly_salary + benefits + equipment + infrastructure)
        
        return {
            "total": total,
            "breakdown": {
                "salary": monthly_salary * num_agents,
                "benefits": benefits * num_agents,
                "equipment": equipment * num_agents,
                "infrastructure": infrastructure * num_agents
            }
        }

    def _calculate_indirect_costs(self, num_agents: int, calls_per_month: int) -> Dict[str, float]:
        """Calculate indirect costs including management, training, and quality assurance"""
        management_cost = 1000 * (num_agents / 10)  # One manager per 10 agents
        training_cost = 500 * num_agents  # Monthly training cost per agent
        qa_cost = 0.5 * calls_per_month  # QA cost per call
        admin_cost = 200 * num_agents  # Administrative overhead per agent
        
        total = management_cost + training_cost + qa_cost + admin_cost
        
        return {
            "total": total,
            "breakdown": {
                "management": management_cost,
                "training": training_cost,
                "quality_assurance": qa_cost,
                "administrative": admin_cost
            }
        }

    def _calculate_opportunity_costs(self, num_agents: int, calls_per_month: int) -> Dict[str, float]:
        """Calculate opportunity costs from inefficiencies and missed opportunities"""
        avg_utilization = 0.75  # Average agent utilization rate
        missed_calls = calls_per_month * (1 - avg_utilization)
        missed_opportunity_cost = missed_calls * 5  # Assumed value per missed call
        
        inefficiency_cost = num_agents * 500  # Monthly cost of agent inefficiency
        scalability_limitation_cost = calls_per_month * 0.1  # Cost of limited scalability
        
        total = missed_opportunity_cost + inefficiency_cost + scalability_limitation_cost
        
        return {
            "total": total,
            "breakdown": {
                "missed_opportunities": missed_opportunity_cost,
                "inefficiency": inefficiency_cost,
                "scalability_limitations": scalability_limitation_cost
            }
        }

    def _calculate_industry_specific_costs(self, industry: str, num_agents: int, calls_per_month: int) -> Dict[str, float]:
        """Calculate industry-specific costs"""
        industry_costs = {
            "financial_services": {
                "compliance_monitoring": 2.0 * calls_per_month,
                "regulatory_training": 1000 * num_agents,
                "audit_requirements": 500 * num_agents
            },
            "healthcare": {
                "hipaa_compliance": 1.5 * calls_per_month,
                "specialized_training": 800 * num_agents,
                "data_security": 600 * num_agents
            },
            "real_estate": {
                "license_maintenance": 300 * num_agents,
                "market_data_access": 200 * num_agents,
                "scheduling_software": 100 * num_agents
            },
            "technology": {
                "technical_training": 1200 * num_agents,
                "software_licenses": 400 * num_agents,
                "technical_support": 300 * num_agents
            }
        }
        
        industry_specific = industry_costs.get(industry.lower(), {})
        total = sum(industry_specific.values())
        
        return {
            "total": total,
            "breakdown": industry_specific
        }

    def _get_benchmark_comparison(self, cost_per_call: float) -> Dict[str, Any]:
        """Compare costs against industry benchmarks"""
        benchmark = self.industry_benchmarks["cost_per_call"]
        
        percentile = statistics.percentileofscore(
            [benchmark["low"], benchmark["average"], benchmark["high"]],
            cost_per_call
        )
        
        return {
            "industry_benchmarks": benchmark,
            "current_cost": cost_per_call,
            "percentile": percentile,
            "standing": "Low" if cost_per_call <= benchmark["low"]
                       else "High" if cost_per_call >= benchmark["high"]
                       else "Average"
        }

    def _get_competitive_analysis(self, current_cost_per_call: float) -> Dict[str, Any]:
        """Analyze costs against competitor solutions"""
        comparisons = {}
        
        for competitor, profile in self.competitors.items():
            savings_percentage = ((profile.avg_cost_per_call - current_cost_per_call)
                               / profile.avg_cost_per_call * 100)
            
            comparisons[competitor] = {
                "their_cost": profile.avg_cost_per_call,
                "savings_percentage": round(savings_percentage, 1),
                "features": profile.features,
                "limitations": profile.limitations,
                "market_focus": profile.market_focus
            }
        
        return comparisons 