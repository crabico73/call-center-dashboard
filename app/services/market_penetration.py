from typing import Dict, Any, List
from dataclasses import dataclass
from decimal import Decimal
import math
from enum import Enum

@dataclass
class CompetitorData:
    name: str
    market_share: float
    growth_rate: float
    pricing_tier: str
    customer_satisfaction: float
    churn_rate: float

@dataclass
class MarketConditions:
    economic_growth: float
    industry_growth: float
    technology_adoption_rate: float
    regulatory_environment: float  # 0-1 scale, 1 being most favorable
    market_consolidation: float   # 0-1 scale, 1 being most consolidated

@dataclass
class PenetrationFactors:
    price_sensitivity: float
    technology_readiness: float
    regulatory_compliance: float
    decision_cycle: int  # months
    integration_complexity: float

class MarketPenetrationService:
    def __init__(self):
        self.adoption_curves = {
            "innovators": 0.025,
            "early_adopters": 0.135,
            "early_majority": 0.34,
            "late_majority": 0.34,
            "laggards": 0.16
        }
        
        self.industry_adoption_speeds = {
            "FINANCIAL": 1.2,      # Faster adoption due to cost pressure
            "HEALTHCARE": 0.8,     # Slower due to regulations
            "REAL_ESTATE": 1.0,    # Average adoption speed
            "TECHNOLOGY": 1.5,     # Fastest adoption
            "RETAIL": 1.1,
            "MANUFACTURING": 0.9,
            "EDUCATION": 0.7,
            "PROFESSIONAL_SERVICES": 1.3
        }
        
        self.market_entry_strategies = {
            "FINANCIAL": {
                "initial_focus": ["cost_reduction", "compliance", "efficiency"],
                "key_differentiators": ["regulatory_compliance", "security", "accuracy"],
                "partnership_approach": ["technology_vendors", "compliance_firms"],
                "pilot_program_length": 3  # months
            },
            "HEALTHCARE": {
                "initial_focus": ["patient_experience", "hipaa_compliance", "scheduling"],
                "key_differentiators": ["phi_protection", "integration", "accuracy"],
                "partnership_approach": ["healthcare_systems", "insurance_providers"],
                "pilot_program_length": 4  # months
            },
            "REAL_ESTATE": {
                "initial_focus": ["lead_response", "availability", "follow_up"],
                "key_differentiators": ["24_7_availability", "personalization", "speed"],
                "partnership_approach": ["brokerages", "property_management_firms"],
                "pilot_program_length": 2  # months
            },
            "TECHNOLOGY": {
                "initial_focus": ["scalability", "integration", "customization"],
                "key_differentiators": ["api_access", "customization", "analytics"],
                "partnership_approach": ["system_integrators", "tech_consultants"],
                "pilot_program_length": 2  # months
            }
        }

    def analyze_market_penetration(self,
                                 industry: str,
                                 market_conditions: MarketConditions,
                                 competitors: List[CompetitorData],
                                 penetration_factors: PenetrationFactors,
                                 timeframe_months: int) -> Dict[str, Any]:
        """Calculate detailed market penetration projections"""
        
        # Calculate base penetration rate
        base_rate = self._calculate_base_penetration_rate(
            market_conditions,
            competitors,
            penetration_factors
        )
        
        # Apply industry-specific adoption speed
        industry_speed = self.industry_adoption_speeds.get(industry.upper(), 1.0)
        
        # Calculate monthly penetration curve
        penetration_curve = self._generate_penetration_curve(
            base_rate,
            industry_speed,
            timeframe_months
        )
        
        # Calculate competitor response impact
        competitor_impact = self._analyze_competitor_impact(
            competitors,
            timeframe_months
        )
        
        # Adjust for market conditions
        market_adjusted_curve = self._adjust_for_market_conditions(
            penetration_curve,
            market_conditions,
            competitor_impact
        )
        
        # Calculate conversion probabilities
        conversion_probs = self._calculate_conversion_probabilities(
            industry,
            penetration_factors,
            market_conditions
        )
        
        return {
            "monthly_penetration": [round(x, 4) for x in market_adjusted_curve],
            "total_penetration": round(sum(market_adjusted_curve), 4),
            "conversion_probabilities": conversion_probs,
            "market_entry_strategy": self.market_entry_strategies.get(industry.upper(), {}),
            "adoption_phases": self._calculate_adoption_phases(market_adjusted_curve),
            "risk_factors": self._analyze_risk_factors(
                industry,
                market_conditions,
                penetration_factors
            ),
            "opportunity_score": self._calculate_opportunity_score(
                market_conditions,
                competitor_impact,
                conversion_probs
            )
        }

    def _calculate_base_penetration_rate(self,
                                       market_conditions: MarketConditions,
                                       competitors: List[CompetitorData],
                                       factors: PenetrationFactors) -> float:
        """Calculate base market penetration rate"""
        # Market condition impact
        market_impact = (
            market_conditions.economic_growth * 0.2 +
            market_conditions.industry_growth * 0.3 +
            market_conditions.technology_adoption_rate * 0.3 +
            market_conditions.regulatory_environment * 0.1 +
            (1 - market_conditions.market_consolidation) * 0.1
        )
        
        # Competitive pressure
        competitive_pressure = sum(c.market_share for c in competitors)
        competitive_impact = 1 - (competitive_pressure * 0.7)  # Leave room for disruption
        
        # Factor impact
        factor_impact = (
            (1 - factors.price_sensitivity) * 0.3 +
            factors.technology_readiness * 0.3 +
            factors.regulatory_compliance * 0.2 +
            (1 - factors.integration_complexity) * 0.2
        )
        
        base_rate = 0.3 * market_impact * competitive_impact * factor_impact
        return min(0.8, max(0.05, base_rate))  # Cap between 5% and 80%

    def _generate_penetration_curve(self,
                                  base_rate: float,
                                  industry_speed: float,
                                  timeframe_months: int) -> List[float]:
        """Generate monthly penetration curve using modified Bass diffusion model"""
        p = 0.03 * industry_speed  # innovation coefficient
        q = 0.4 * industry_speed   # imitation coefficient
        
        curve = []
        cumulative = 0
        
        for t in range(timeframe_months):
            # Modified Bass diffusion formula
            adoption = base_rate * (
                (p + q * cumulative) * (1 - cumulative)
            )
            curve.append(adoption)
            cumulative += adoption
        
        return curve

    def _analyze_competitor_impact(self,
                                 competitors: List[CompetitorData],
                                 timeframe_months: int) -> Dict[str, Any]:
        """Analyze competitive landscape impact"""
        total_market_share = sum(c.market_share for c in competitors)
        weighted_growth = sum(c.market_share * c.growth_rate for c in competitors)
        avg_satisfaction = sum(c.customer_satisfaction * c.market_share 
                             for c in competitors) / total_market_share if total_market_share > 0 else 0
        
        churn_opportunity = sum(c.market_share * c.churn_rate for c in competitors)
        
        return {
            "market_concentration": total_market_share,
            "growth_trajectory": weighted_growth,
            "satisfaction_gap": 1 - avg_satisfaction,
            "churn_opportunity": churn_opportunity,
            "monthly_impact": [
                round(churn_opportunity * (1 + weighted_growth) ** (m/12), 4)
                for m in range(timeframe_months)
            ]
        }

    def _adjust_for_market_conditions(self,
                                    base_curve: List[float],
                                    conditions: MarketConditions,
                                    competitor_impact: Dict[str, Any]) -> List[float]:
        """Adjust penetration curve for market conditions"""
        adjusted_curve = []
        
        for month, base_rate in enumerate(base_curve):
            # Economic adjustment
            economic_factor = 1 + (conditions.economic_growth * 0.5)
            
            # Industry growth adjustment
            industry_factor = 1 + (conditions.industry_growth * 0.3)
            
            # Technology adoption adjustment
            tech_factor = 1 + (conditions.technology_adoption_rate * 0.4)
            
            # Competitive adjustment
            competitive_factor = 1 + competitor_impact["monthly_impact"][month]
            
            # Combined adjustment
            adjustment = economic_factor * industry_factor * tech_factor * competitive_factor
            
            adjusted_curve.append(base_rate * adjustment)
        
        return adjusted_curve

    def _calculate_conversion_probabilities(self,
                                         industry: str,
                                         factors: PenetrationFactors,
                                         conditions: MarketConditions) -> Dict[str, float]:
        """Calculate conversion probabilities for different stages"""
        base_conversion = 0.2  # 20% base conversion rate
        
        # Industry-specific adjustment
        industry_factor = self.industry_adoption_speeds.get(industry.upper(), 1.0)
        
        # Price sensitivity impact
        price_impact = 1 - (factors.price_sensitivity * 0.5)
        
        # Technology readiness impact
        tech_impact = 1 + (factors.technology_readiness * 0.3)
        
        # Market condition impact
        market_impact = 1 + (conditions.industry_growth * 0.4)
        
        # Calculate stage-specific probabilities
        adjusted_base = base_conversion * industry_factor * price_impact * tech_impact * market_impact
        
        return {
            "initial_contact": round(adjusted_base, 3),
            "demo_booking": round(adjusted_base * 0.7, 3),
            "demo_completion": round(adjusted_base * 0.8, 3),
            "proposal_acceptance": round(adjusted_base * 0.6, 3),
            "contract_signing": round(adjusted_base * 0.5, 3)
        }

    def _calculate_adoption_phases(self, penetration_curve: List[float]) -> Dict[str, Any]:
        """Calculate adoption phases based on penetration curve"""
        cumulative = 0
        phases = {
            "innovators": None,
            "early_adopters": None,
            "early_majority": None,
            "late_majority": None,
            "laggards": None
        }
        
        for month, rate in enumerate(penetration_curve):
            cumulative += rate
            
            for phase, threshold in self.adoption_curves.items():
                if phases[phase] is None and cumulative >= threshold:
                    phases[phase] = month + 1
        
        return {
            "phase_transitions": phases,
            "current_phase": self._determine_current_phase(cumulative)
        }

    def _analyze_risk_factors(self,
                            industry: str,
                            conditions: MarketConditions,
                            factors: PenetrationFactors) -> Dict[str, Any]:
        """Analyze risk factors affecting market penetration"""
        risks = {
            "market_risks": {
                "economic_volatility": 1 - conditions.economic_growth,
                "market_consolidation": conditions.market_consolidation,
                "regulatory_changes": 1 - conditions.regulatory_environment
            },
            "adoption_risks": {
                "price_sensitivity": factors.price_sensitivity,
                "integration_complexity": factors.integration_complexity,
                "technology_resistance": 1 - factors.technology_readiness
            },
            "competitive_risks": {
                "market_saturation": conditions.market_consolidation,
                "price_pressure": factors.price_sensitivity,
                "technology_disruption": conditions.technology_adoption_rate
            }
        }
        
        # Calculate risk scores
        risk_scores = {
            category: round(sum(values.values()) / len(values), 2)
            for category, values in risks.items()
        }
        
        return {
            "detailed_risks": risks,
            "risk_scores": risk_scores,
            "overall_risk_score": round(sum(risk_scores.values()) / len(risk_scores), 2)
        }

    def _calculate_opportunity_score(self,
                                  conditions: MarketConditions,
                                  competitor_impact: Dict[str, Any],
                                  conversion_probs: Dict[str, float]) -> float:
        """Calculate overall opportunity score"""
        # Market conditions score (0-100)
        market_score = (
            conditions.economic_growth * 20 +
            conditions.industry_growth * 30 +
            conditions.technology_adoption_rate * 30 +
            conditions.regulatory_environment * 20
        ) * 100
        
        # Competitive opportunity score (0-100)
        competitive_score = (
            competitor_impact["satisfaction_gap"] * 40 +
            competitor_impact["churn_opportunity"] * 60
        ) * 100
        
        # Conversion potential score (0-100)
        conversion_score = (
            conversion_probs["initial_contact"] * 20 +
            conversion_probs["demo_completion"] * 30 +
            conversion_probs["contract_signing"] * 50
        ) * 100
        
        # Weighted average
        opportunity_score = (
            market_score * 0.4 +
            competitive_score * 0.3 +
            conversion_score * 0.3
        )
        
        return round(opportunity_score, 1)

    def _determine_current_phase(self, cumulative_penetration: float) -> str:
        """Determine current adoption phase"""
        thresholds = list(self.adoption_curves.items())
        current_phase = thresholds[-1][0]  # Default to last phase
        
        cumulative = 0
        for phase, threshold in thresholds:
            cumulative += threshold
            if cumulative_penetration <= cumulative:
                current_phase = phase
                break
        
        return current_phase 