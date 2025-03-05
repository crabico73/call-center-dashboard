from typing import Dict, Any, List
from dataclasses import dataclass
from decimal import Decimal
import numpy as np
from datetime import datetime, timedelta

@dataclass
class ROIScenario:
    name: str
    description: str
    assumptions: Dict[str, Any]
    multipliers: Dict[str, float]

class AdvancedROICalculator:
    def __init__(self):
        self.scenarios = {
            "conservative": ROIScenario(
                name="Conservative",
                description="Minimal performance improvements, focused on direct cost savings",
                assumptions={
                    "efficiency_gain": 0.2,
                    "quality_improvement": 0.1,
                    "conversion_boost": 0.05
                },
                multipliers={
                    "cost_reduction": 0.4,
                    "revenue_increase": 0.1,
                    "productivity_gain": 0.2
                }
            ),
            "moderate": ROIScenario(
                name="Moderate",
                description="Balanced improvements across all areas",
                assumptions={
                    "efficiency_gain": 0.35,
                    "quality_improvement": 0.25,
                    "conversion_boost": 0.15
                },
                multipliers={
                    "cost_reduction": 0.5,
                    "revenue_increase": 0.2,
                    "productivity_gain": 0.35
                }
            ),
            "aggressive": ROIScenario(
                name="Aggressive",
                description="Maximum potential benefits with optimal implementation",
                assumptions={
                    "efficiency_gain": 0.5,
                    "quality_improvement": 0.4,
                    "conversion_boost": 0.25
                },
                multipliers={
                    "cost_reduction": 0.6,
                    "revenue_increase": 0.3,
                    "productivity_gain": 0.5
                }
            )
        }

    def calculate_comprehensive_roi(self,
                                 current_costs: Dict[str, float],
                                 operational_metrics: Dict[str, Any],
                                 selected_tier: Dict[str, Any],
                                 industry: str,
                                 scenario: str = "moderate") -> Dict[str, Any]:
        """Calculate comprehensive ROI with multiple scenarios"""
        
        # Get scenario configuration
        scenario_config = self.scenarios.get(scenario.lower())
        if not scenario_config:
            raise ValueError(f"Invalid scenario: {scenario}")
        
        # Calculate base savings
        base_savings = self._calculate_base_savings(
            current_costs,
            selected_tier,
            scenario_config
        )
        
        # Calculate operational improvements
        operational_benefits = self._calculate_operational_benefits(
            operational_metrics,
            scenario_config
        )
        
        # Calculate industry-specific benefits
        industry_benefits = self._calculate_industry_benefits(
            industry,
            current_costs,
            scenario_config
        )
        
        # Project cash flows
        cash_flows = self._project_cash_flows(
            base_savings,
            operational_benefits,
            industry_benefits,
            selected_tier
        )
        
        # Calculate ROI metrics
        roi_metrics = self._calculate_roi_metrics(cash_flows, selected_tier)
        
        return {
            "summary": {
                "total_annual_savings": round(base_savings["annual"] + 
                                           operational_benefits["annual"] +
                                           industry_benefits["annual"], 2),
                "roi_percentage": roi_metrics["roi_percentage"],
                "payback_period_months": roi_metrics["payback_period"],
                "npv": roi_metrics["npv"],
                "irr": roi_metrics["irr"]
            },
            "detailed_benefits": {
                "base_savings": base_savings,
                "operational_benefits": operational_benefits,
                "industry_benefits": industry_benefits
            },
            "projections": {
                "monthly_cash_flows": cash_flows["monthly"],
                "cumulative_savings": cash_flows["cumulative"],
                "break_even_point": cash_flows["break_even"]
            },
            "scenario_analysis": {
                "name": scenario_config.name,
                "description": scenario_config.description,
                "assumptions": scenario_config.assumptions,
                "risk_factors": self._analyze_risk_factors(scenario_config)
            }
        }

    def _calculate_base_savings(self,
                              current_costs: Dict[str, float],
                              selected_tier: Dict[str, Any],
                              scenario: ROIScenario) -> Dict[str, float]:
        """Calculate direct cost savings"""
        monthly_cost_reduction = (current_costs["total_monthly_cost"] * 
                                scenario.multipliers["cost_reduction"])
        
        return {
            "monthly": round(monthly_cost_reduction, 2),
            "annual": round(monthly_cost_reduction * 12, 2),
            "five_year": round(monthly_cost_reduction * 12 * 5, 2),
            "categories": {
                "direct_labor": round(monthly_cost_reduction * 0.6, 2),
                "overhead": round(monthly_cost_reduction * 0.2, 2),
                "training": round(monthly_cost_reduction * 0.1, 2),
                "other": round(monthly_cost_reduction * 0.1, 2)
            }
        }

    def _calculate_operational_benefits(self,
                                     metrics: Dict[str, Any],
                                     scenario: ROIScenario) -> Dict[str, float]:
        """Calculate operational improvement benefits"""
        base_efficiency_value = metrics.get("calls_per_month", 0) * 2  # $2 value per call
        productivity_gain = base_efficiency_value * scenario.assumptions["efficiency_gain"]
        
        quality_improvement_value = (metrics.get("calls_per_month", 0) * 
                                   scenario.assumptions["quality_improvement"] * 1.5)
        
        conversion_value = (metrics.get("calls_per_month", 0) * 
                          scenario.assumptions["conversion_boost"] * 5)
        
        monthly_benefit = productivity_gain + quality_improvement_value + conversion_value
        
        return {
            "monthly": round(monthly_benefit, 2),
            "annual": round(monthly_benefit * 12, 2),
            "five_year": round(monthly_benefit * 12 * 5, 2),
            "categories": {
                "productivity": round(productivity_gain, 2),
                "quality": round(quality_improvement_value, 2),
                "conversion": round(conversion_value, 2)
            }
        }

    def _calculate_industry_benefits(self,
                                   industry: str,
                                   current_costs: Dict[str, float],
                                   scenario: ROIScenario) -> Dict[str, float]:
        """Calculate industry-specific benefits"""
        industry_factors = {
            "financial_services": {
                "compliance_value": 0.15,
                "risk_reduction": 0.10,
                "audit_efficiency": 0.05
            },
            "healthcare": {
                "hipaa_compliance": 0.20,
                "patient_satisfaction": 0.10,
                "record_accuracy": 0.05
            },
            "real_estate": {
                "lead_response": 0.15,
                "follow_up": 0.10,
                "scheduling": 0.05
            },
            "technology": {
                "technical_accuracy": 0.10,
                "demo_efficiency": 0.10,
                "integration": 0.10
            }
        }
        
        industry_multipliers = industry_factors.get(industry.lower(), {})
        monthly_benefit = sum(
            current_costs["total_monthly_cost"] * value * scenario.multipliers["revenue_increase"]
            for value in industry_multipliers.values()
        )
        
        return {
            "monthly": round(monthly_benefit, 2),
            "annual": round(monthly_benefit * 12, 2),
            "five_year": round(monthly_benefit * 12 * 5, 2),
            "categories": {
                factor: round(current_costs["total_monthly_cost"] * value * 
                            scenario.multipliers["revenue_increase"], 2)
                for factor, value in industry_multipliers.items()
            }
        }

    def _project_cash_flows(self,
                          base_savings: Dict[str, float],
                          operational_benefits: Dict[str, float],
                          industry_benefits: Dict[str, float],
                          selected_tier: Dict[str, Any]) -> Dict[str, Any]:
        """Project monthly cash flows and calculate break-even point"""
        monthly_benefit = (base_savings["monthly"] + 
                         operational_benefits["monthly"] +
                         industry_benefits["monthly"])
        
        setup_cost = float(selected_tier["setup_fee"])
        monthly_cost = float(selected_tier["price_per_month"])
        
        monthly_flows = []
        cumulative = -setup_cost
        break_even_month = None
        
        for month in range(1, 61):  # 5 years projection
            net_flow = monthly_benefit - monthly_cost
            cumulative += net_flow
            monthly_flows.append(round(net_flow, 2))
            
            if break_even_month is None and cumulative > 0:
                break_even_month = month
        
        return {
            "monthly": monthly_flows,
            "cumulative": round(cumulative, 2),
            "break_even": break_even_month
        }

    def _calculate_roi_metrics(self,
                             cash_flows: Dict[str, Any],
                             selected_tier: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key ROI metrics including NPV and IRR"""
        initial_investment = float(selected_tier["setup_fee"])
        monthly_flows = cash_flows["monthly"]
        
        # Calculate NPV
        discount_rate = 0.10  # 10% annual discount rate
        monthly_rate = (1 + discount_rate) ** (1/12) - 1
        
        npv = -initial_investment + sum(
            flow / (1 + monthly_rate) ** (i+1)
            for i, flow in enumerate(monthly_flows)
        )
        
        # Calculate IRR (simplified)
        irr = (sum(monthly_flows) - initial_investment) / initial_investment / 5  # 5 years
        
        return {
            "roi_percentage": round((sum(monthly_flows) - initial_investment) / 
                                  initial_investment * 100, 2),
            "payback_period": cash_flows["break_even"],
            "npv": round(npv, 2),
            "irr": round(irr * 100, 2)
        }

    def _analyze_risk_factors(self, scenario: ROIScenario) -> Dict[str, Any]:
        """Analyze risk factors based on scenario assumptions"""
        risk_levels = {
            "conservative": {
                "implementation_risk": "Low",
                "adoption_risk": "Low",
                "performance_risk": "Low"
            },
            "moderate": {
                "implementation_risk": "Medium",
                "adoption_risk": "Medium",
                "performance_risk": "Medium"
            },
            "aggressive": {
                "implementation_risk": "High",
                "adoption_risk": "High",
                "performance_risk": "High"
            }
        }
        
        return risk_levels.get(scenario.name.lower(), risk_levels["moderate"]) 