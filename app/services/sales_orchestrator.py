from typing import Dict, Any
from app.services.cost_analysis_service import AdvancedCostAnalysisService
from app.services.roi_calculator import AdvancedROICalculator
from app.services.industry_tracks import IndustryTracksService
from app.core.default_agent import DEFAULT_AGENT_CONFIG

class SalesOrchestrator:
    def __init__(self):
        self.cost_analyzer = AdvancedCostAnalysisService()
        self.roi_calculator = AdvancedROICalculator()
        self.industry_tracks = IndustryTracksService()
        
    def prepare_sales_strategy(self,
                             company_info: Dict[str, Any],
                             call_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive sales strategy based on company profile"""
        
        # Get industry-specific track
        industry_track = self.industry_tracks.get_industry_track(company_info["industry"])
        
        # Analyze current costs
        cost_analysis = self.cost_analyzer.analyze_total_cost_of_ownership(
            num_agents=company_info["num_agents"],
            calls_per_month=call_metrics["monthly_volume"],
            avg_agent_salary=company_info.get("avg_agent_salary"),
            industry=company_info["industry"]
        )
        
        # Get subscription recommendation
        subscription = self.cost_analyzer.recommend_subscription(
            current_monthly_calls=call_metrics["monthly_volume"],
            current_monthly_cost=cost_analysis["total_monthly_cost"]
        )
        
        # Calculate ROI projections
        roi_analysis = self.roi_calculator.calculate_comprehensive_roi(
            current_costs=cost_analysis,
            operational_metrics=call_metrics,
            selected_tier=subscription["recommendation"],
            industry=company_info["industry"]
        )
        
        # Generate conversation strategy
        conversation_strategy = self._generate_conversation_strategy(
            industry_track,
            cost_analysis,
            subscription,
            roi_analysis
        )
        
        return {
            "industry_track": industry_track,
            "cost_analysis": cost_analysis,
            "subscription": subscription,
            "roi_analysis": roi_analysis,
            "conversation_strategy": conversation_strategy
        }
    
    def _generate_conversation_strategy(self,
                                     industry_track: Dict[str, Any],
                                     cost_analysis: Dict[str, Any],
                                     subscription: Dict[str, Any],
                                     roi_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tailored conversation strategy"""
        
        # Key talking points based on cost analysis
        cost_points = [
            f"Current cost per call: ${cost_analysis['cost_per_call']}",
            f"Potential cost reduction: {subscription['cost_reduction_percentage']}%",
            f"Annual savings: ${roi_analysis['summary']['total_annual_savings']:,.2f}",
            f"ROI timeline: {roi_analysis['summary']['payback_period_months']} months"
        ]
        
        # Industry-specific value propositions
        value_props = [
            f"Industry benchmark comparison: {cost_analysis['benchmarks']['standing']}",
            *industry_track.value_props
        ]
        
        # Competitive advantages
        competitive_edges = []
        for competitor, analysis in cost_analysis["competitive_analysis"].items():
            if analysis["savings_percentage"] > 0:
                competitive_edges.append(
                    f"{analysis['savings_percentage']}% savings vs {competitor}"
                )
        
        # ROI highlights
        roi_highlights = [
            f"NPV of investment: ${roi_analysis['summary']['npv']:,.2f}",
            f"IRR: {roi_analysis['summary']['irr']}%",
            f"5-year savings: ${roi_analysis['detailed_benefits']['base_savings']['five_year']:,.2f}"
        ]
        
        # Conversation flow
        conversation_flow = {
            "qualification": {
                "questions": industry_track.conversation_hooks,
                "metrics_to_gather": industry_track.key_metrics
            },
            "pain_points": {
                "industry_specific": industry_track.pain_points,
                "cost_related": [
                    "High agent turnover",
                    "Training costs",
                    "Quality inconsistency",
                    "Limited scalability"
                ]
            },
            "value_demonstration": {
                "cost_savings": cost_points,
                "industry_benefits": value_props,
                "competitive_advantages": competitive_edges,
                "roi_metrics": roi_highlights
            },
            "objection_handling": {
                "cost": [
                    f"Investment pays for itself in {roi_analysis['summary']['payback_period_months']} months",
                    f"Guaranteed {subscription['cost_reduction_percentage']}% cost reduction"
                ],
                "quality": [
                    "100% consistent performance",
                    "Zero quality variations",
                    "Perfect compliance"
                ],
                "implementation": [
                    f"{subscription['recommendation'].setup_period} days setup",
                    "Minimal disruption",
                    "Comprehensive support"
                ]
            }
        }
        
        return {
            "key_metrics": industry_track.key_metrics,
            "pain_points": industry_track.pain_points,
            "value_props": value_props,
            "cost_points": cost_points,
            "roi_highlights": roi_highlights,
            "competitive_edges": competitive_edges,
            "conversation_flow": conversation_flow,
            "closing_triggers": {
                "cost_sensitivity": "ROI timeline",
                "quality_focus": "Perfect consistency",
                "compliance_priority": "Zero violations",
                "scalability_needs": "Unlimited capacity"
            }
        } 