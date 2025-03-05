from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics

class ImplementationPhase(Enum):
    INITIAL_CONTACT = "initial_contact"
    REQUIREMENTS_GATHERING = "requirements_gathering"
    CONTRACT_NEGOTIATION = "contract_negotiation"
    SYSTEM_SETUP = "system_setup"
    INTEGRATION = "integration"
    TESTING = "testing"
    GO_LIVE = "go_live"
    OPTIMIZATION = "optimization"

class MetricType(Enum):
    TIME_TO_VALUE = "time_to_value"
    COST_SAVINGS = "cost_savings"
    EFFICIENCY_GAINS = "efficiency_gains"
    QUALITY_IMPROVEMENTS = "quality_improvements"
    ROI = "roi"

@dataclass
class ImplementationMetrics:
    client_id: str
    industry: str
    start_date: datetime
    completion_date: Optional[datetime]
    subscription_tier: str
    initial_call_volume: int
    phase_durations: Dict[str, timedelta]
    traditional_costs: Dict[str, float]
    actual_costs: Dict[str, float]
    efficiency_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]

class ROITrackingService:
    def __init__(self):
        self.implementation_data: Dict[str, ImplementationMetrics] = {}
        self.industry_benchmarks: Dict[str, Dict[str, Any]] = {}
        
    def start_tracking(self,
                      client_id: str,
                      industry: str,
                      subscription_tier: str,
                      initial_call_volume: int,
                      traditional_costs: Dict[str, float]) -> Dict[str, Any]:
        """Initialize tracking for a new implementation"""
        
        metrics = ImplementationMetrics(
            client_id=client_id,
            industry=industry,
            start_date=datetime.now(),
            completion_date=None,
            subscription_tier=subscription_tier,
            initial_call_volume=initial_call_volume,
            phase_durations={},
            traditional_costs=traditional_costs,
            actual_costs={},
            efficiency_metrics={},
            quality_metrics={}
        )
        
        self.implementation_data[client_id] = metrics
        
        return {
            "tracking_id": client_id,
            "start_date": metrics.start_date.isoformat(),
            "initial_metrics": {
                "industry": industry,
                "subscription_tier": subscription_tier,
                "call_volume": initial_call_volume,
                "traditional_costs": traditional_costs
            }
        }

    def record_phase_completion(self,
                              client_id: str,
                              phase: ImplementationPhase,
                              actual_costs: Dict[str, float],
                              metrics: Dict[str, float]) -> Dict[str, Any]:
        """Record the completion of an implementation phase"""
        
        if client_id not in self.implementation_data:
            raise ValueError("Client tracking not initialized")
        
        implementation = self.implementation_data[client_id]
        phase_start = implementation.start_date
        
        if implementation.phase_durations:
            # Get the last completed phase's end time
            last_phase_end = implementation.start_date + sum(
                implementation.phase_durations.values(),
                timedelta()
            )
            phase_start = last_phase_end
        
        duration = datetime.now() - phase_start
        implementation.phase_durations[phase.value] = duration
        
        # Update costs and metrics
        implementation.actual_costs.update(actual_costs)
        if phase == ImplementationPhase.GO_LIVE:
            implementation.completion_date = datetime.now()
        
        # Update efficiency and quality metrics
        if "efficiency_rate" in metrics:
            implementation.efficiency_metrics[phase.value] = metrics["efficiency_rate"]
        if "quality_score" in metrics:
            implementation.quality_metrics[phase.value] = metrics["quality_score"]
        
        return self._calculate_current_metrics(client_id)

    def get_roi_analysis(self, client_id: str) -> Dict[str, Any]:
        """Generate comprehensive ROI analysis"""
        
        if client_id not in self.implementation_data:
            raise ValueError("Client tracking not initialized")
        
        implementation = self.implementation_data[client_id]
        
        # Calculate total time to value
        total_duration = sum(
            implementation.phase_durations.values(),
            timedelta()
        )
        
        # Calculate cost savings
        traditional_total = sum(implementation.traditional_costs.values())
        actual_total = sum(implementation.actual_costs.values())
        savings = traditional_total - actual_total
        
        # Calculate efficiency gains
        efficiency_improvement = 0
        if implementation.efficiency_metrics:
            efficiency_improvement = (
                statistics.mean(implementation.efficiency_metrics.values()) * 100
            )
        
        # Calculate quality improvements
        quality_improvement = 0
        if implementation.quality_metrics:
            quality_improvement = (
                statistics.mean(implementation.quality_metrics.values()) * 100
            )
        
        # Calculate ROI
        roi = (savings / actual_total * 100) if actual_total > 0 else 0
        
        return {
            "client_id": client_id,
            "industry": implementation.industry,
            "implementation_summary": {
                "start_date": implementation.start_date.isoformat(),
                "completion_date": implementation.completion_date.isoformat() if implementation.completion_date else None,
                "total_duration_days": total_duration.days,
                "phase_breakdown": {
                    phase: duration.days
                    for phase, duration in implementation.phase_durations.items()
                }
            },
            "cost_analysis": {
                "traditional_costs": implementation.traditional_costs,
                "actual_costs": implementation.actual_costs,
                "total_savings": savings,
                "savings_percentage": (savings / traditional_total * 100) if traditional_total > 0 else 0
            },
            "performance_metrics": {
                "efficiency_improvement": efficiency_improvement,
                "quality_improvement": quality_improvement,
                "roi_percentage": roi
            },
            "benchmarks": self._get_industry_benchmarks(implementation.industry)
        }

    def update_industry_benchmarks(self) -> Dict[str, Dict[str, Any]]:
        """Update industry benchmarks based on collected data"""
        
        benchmarks = {}
        for client_id, implementation in self.implementation_data.items():
            industry = implementation.industry
            
            if industry not in benchmarks:
                benchmarks[industry] = {
                    "avg_implementation_days": 0,
                    "avg_cost_savings": 0,
                    "avg_efficiency_gain": 0,
                    "avg_quality_improvement": 0,
                    "avg_roi": 0,
                    "sample_size": 0
                }
            
            # Skip incomplete implementations
            if not implementation.completion_date:
                continue
            
            current = benchmarks[industry]
            current["sample_size"] += 1
            n = current["sample_size"]
            
            # Calculate running averages
            total_duration = sum(implementation.phase_durations.values(), timedelta())
            current["avg_implementation_days"] = self._running_average(
                current["avg_implementation_days"],
                total_duration.days,
                n
            )
            
            traditional_total = sum(implementation.traditional_costs.values())
            actual_total = sum(implementation.actual_costs.values())
            savings_pct = ((traditional_total - actual_total) / traditional_total * 100
                         if traditional_total > 0 else 0)
            current["avg_cost_savings"] = self._running_average(
                current["avg_cost_savings"],
                savings_pct,
                n
            )
            
            if implementation.efficiency_metrics:
                efficiency_gain = statistics.mean(implementation.efficiency_metrics.values()) * 100
                current["avg_efficiency_gain"] = self._running_average(
                    current["avg_efficiency_gain"],
                    efficiency_gain,
                    n
                )
            
            if implementation.quality_metrics:
                quality_improvement = statistics.mean(implementation.quality_metrics.values()) * 100
                current["avg_quality_improvement"] = self._running_average(
                    current["avg_quality_improvement"],
                    quality_improvement,
                    n
                )
            
            roi = (savings_pct * actual_total / traditional_total
                  if traditional_total > 0 else 0)
            current["avg_roi"] = self._running_average(
                current["avg_roi"],
                roi,
                n
            )
        
        self.industry_benchmarks = benchmarks
        return benchmarks

    def _calculate_current_metrics(self, client_id: str) -> Dict[str, Any]:
        """Calculate current implementation metrics"""
        
        implementation = self.implementation_data[client_id]
        current_duration = sum(implementation.phase_durations.values(), timedelta())
        
        traditional_costs = sum(implementation.traditional_costs.values())
        actual_costs = sum(implementation.actual_costs.values())
        current_savings = traditional_costs - actual_costs
        
        return {
            "current_phase": self._get_current_phase(implementation),
            "elapsed_time_days": current_duration.days,
            "cost_metrics": {
                "traditional_cost_to_date": traditional_costs,
                "actual_cost_to_date": actual_costs,
                "current_savings": current_savings,
                "savings_percentage": (current_savings / traditional_costs * 100
                                    if traditional_costs > 0 else 0)
            },
            "performance_metrics": {
                "latest_efficiency": self._get_latest_metric(implementation.efficiency_metrics),
                "latest_quality": self._get_latest_metric(implementation.quality_metrics)
            }
        }

    def _get_current_phase(self, implementation: ImplementationMetrics) -> str:
        """Determine the current implementation phase"""
        completed_phases = set(implementation.phase_durations.keys())
        for phase in ImplementationPhase:
            if phase.value not in completed_phases:
                return phase.value
        return ImplementationPhase.OPTIMIZATION.value

    def _get_latest_metric(self, metrics: Dict[str, float]) -> Optional[float]:
        """Get the most recent metric value"""
        if not metrics:
            return None
        return metrics[max(metrics.keys())]

    def _get_industry_benchmarks(self, industry: str) -> Dict[str, Any]:
        """Get benchmarks for a specific industry"""
        return self.industry_benchmarks.get(industry, {})

    @staticmethod
    def _running_average(current_avg: float, new_value: float, n: int) -> float:
        """Calculate running average"""
        return (current_avg * (n - 1) + new_value) / n 