from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import statistics
from enum import Enum

class ContractMetricType(Enum):
    TOTAL_VALUE = "total_value"
    MONTHLY_VALUE = "monthly_value"
    CONTRACT_TERM = "contract_term"
    INDUSTRY_DISTRIBUTION = "industry_distribution"
    TIER_DISTRIBUTION = "tier_distribution"
    GEOGRAPHIC_DISTRIBUTION = "geographic_distribution"

@dataclass
class HighTierMetrics:
    total_contract_value: float
    monthly_recurring_revenue: float
    average_contract_term: float
    contract_count: int
    industry_breakdown: Dict[str, int]
    tier_breakdown: Dict[str, int]
    geographic_breakdown: Dict[str, int]
    year_to_date_growth: float
    conversion_rate: float

class HighTierAnalyticsService:
    def __init__(self):
        self.contracts: List[Dict[str, Any]] = []
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = {
            metric_type.value: [] for metric_type in ContractMetricType
        }
        
    def track_contract_signed(self,
                            contract_details: Dict[str, Any],
                            customer_info: Dict[str, Any],
                            timestamp: Optional[datetime] = None) -> None:
        """Track a new high-tier contract signing"""
        if not timestamp:
            timestamp = datetime.now()
            
        contract_data = {
            "timestamp": timestamp,
            "contract_details": contract_details,
            "customer_info": customer_info,
            "metrics": self._calculate_contract_metrics(contract_details, customer_info)
        }
        
        self.contracts.append(contract_data)
        self._update_metrics_history(contract_data)

    def _calculate_contract_metrics(self,
                                 contract_details: Dict[str, Any],
                                 customer_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key metrics for a contract"""
        contract_value = contract_details.get('value', {})
        term_months = contract_details.get('terms', {}).get('initial_term_months', 0)
        
        return {
            "total_value": contract_value.get('total', 0),
            "monthly_value": contract_value.get('monthly', 0),
            "term_months": term_months,
            "industry": customer_info.get('industry'),
            "tier": contract_details.get('subscription_tier'),
            "region": customer_info.get('region', 'Unknown'),
            "close_time_days": contract_details.get('sales_cycle_days', 0)
        }

    def _update_metrics_history(self, contract_data: Dict[str, Any]) -> None:
        """Update historical metrics with new contract data"""
        metrics = contract_data['metrics']
        timestamp = contract_data['timestamp']
        
        # Update total value history
        self.metrics_history[ContractMetricType.TOTAL_VALUE.value].append({
            "timestamp": timestamp,
            "value": metrics['total_value']
        })
        
        # Update monthly value history
        self.metrics_history[ContractMetricType.MONTHLY_VALUE.value].append({
            "timestamp": timestamp,
            "value": metrics['monthly_value']
        })
        
        # Update term length history
        self.metrics_history[ContractMetricType.CONTRACT_TERM.value].append({
            "timestamp": timestamp,
            "value": metrics['term_months']
        })
        
        # Update distribution metrics
        for metric_type, key in [
            (ContractMetricType.INDUSTRY_DISTRIBUTION, 'industry'),
            (ContractMetricType.TIER_DISTRIBUTION, 'tier'),
            (ContractMetricType.GEOGRAPHIC_DISTRIBUTION, 'region')
        ]:
            self.metrics_history[metric_type.value].append({
                "timestamp": timestamp,
                "value": metrics[key]
            })

    def get_current_metrics(self) -> HighTierMetrics:
        """Get current high-tier contract metrics"""
        if not self.contracts:
            return HighTierMetrics(
                total_contract_value=0,
                monthly_recurring_revenue=0,
                average_contract_term=0,
                contract_count=0,
                industry_breakdown={},
                tier_breakdown={},
                geographic_breakdown={},
                year_to_date_growth=0,
                conversion_rate=0
            )
        
        # Calculate current year metrics
        current_year = datetime.now().year
        ytd_contracts = [
            contract for contract in self.contracts
            if contract['timestamp'].year == current_year
        ]
        
        # Calculate year-to-date growth
        previous_year_contracts = [
            contract for contract in self.contracts
            if contract['timestamp'].year == current_year - 1
        ]
        
        ytd_value = sum(c['metrics']['total_value'] for c in ytd_contracts)
        previous_year_value = sum(c['metrics']['total_value'] for c in previous_year_contracts)
        
        ytd_growth = (
            ((ytd_value - previous_year_value) / previous_year_value * 100)
            if previous_year_value > 0 else 0
        )
        
        # Calculate current metrics
        return HighTierMetrics(
            total_contract_value=sum(c['metrics']['total_value'] for c in self.contracts),
            monthly_recurring_revenue=sum(c['metrics']['monthly_value'] for c in self.contracts),
            average_contract_term=statistics.mean(c['metrics']['term_months'] for c in self.contracts),
            contract_count=len(self.contracts),
            industry_breakdown=self._calculate_distribution('industry'),
            tier_breakdown=self._calculate_distribution('tier'),
            geographic_breakdown=self._calculate_distribution('region'),
            year_to_date_growth=ytd_growth,
            conversion_rate=self._calculate_conversion_rate()
        )

    def _calculate_distribution(self, key: str) -> Dict[str, int]:
        """Calculate distribution of contracts by a specific key"""
        distribution = {}
        for contract in self.contracts:
            value = contract['metrics'][key]
            distribution[value] = distribution.get(value, 0) + 1
        return distribution

    def _calculate_conversion_rate(self) -> float:
        """Calculate conversion rate for high-tier contracts"""
        total_opportunities = sum(1 for c in self.contracts if 'sales_cycle_days' in c['metrics'])
        if not total_opportunities:
            return 0
        
        successful_conversions = sum(
            1 for c in self.contracts
            if c['metrics'].get('sales_cycle_days', 0) > 0
        )
        
        return (successful_conversions / total_opportunities) * 100

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for the high-tier contracts dashboard"""
        metrics = self.get_current_metrics()
        
        # Prepare time series data
        time_series_data = {
            "total_value": self._prepare_time_series(ContractMetricType.TOTAL_VALUE),
            "monthly_value": self._prepare_time_series(ContractMetricType.MONTHLY_VALUE),
            "contract_terms": self._prepare_time_series(ContractMetricType.CONTRACT_TERM)
        }
        
        # Prepare distribution data
        distribution_data = {
            "industry": self._prepare_distribution_chart(metrics.industry_breakdown),
            "tier": self._prepare_distribution_chart(metrics.tier_breakdown),
            "geographic": self._prepare_distribution_chart(metrics.geographic_breakdown)
        }
        
        return {
            "summary_metrics": {
                "total_contract_value": metrics.total_contract_value,
                "monthly_recurring_revenue": metrics.monthly_recurring_revenue,
                "average_contract_term": metrics.average_contract_term,
                "contract_count": metrics.contract_count,
                "year_to_date_growth": metrics.year_to_date_growth,
                "conversion_rate": metrics.conversion_rate
            },
            "time_series": time_series_data,
            "distributions": distribution_data,
            "recent_contracts": self._get_recent_contracts(5)
        }

    def _prepare_time_series(self, metric_type: ContractMetricType) -> Dict[str, List[Any]]:
        """Prepare time series data for visualization"""
        data = self.metrics_history[metric_type.value]
        if not data:
            return {"dates": [], "values": []}
            
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        df = df.resample('D').sum()  # Daily aggregation
        
        return {
            "dates": df.index.strftime('%Y-%m-%d').tolist(),
            "values": df['value'].tolist()
        }

    def _prepare_distribution_chart(self, distribution: Dict[str, int]) -> Dict[str, List[Any]]:
        """Prepare distribution data for visualization"""
        return {
            "labels": list(distribution.keys()),
            "values": list(distribution.values())
        }

    def _get_recent_contracts(self, limit: int) -> List[Dict[str, Any]]:
        """Get most recent high-tier contracts"""
        sorted_contracts = sorted(
            self.contracts,
            key=lambda x: x['timestamp'],
            reverse=True
        )
        
        return [{
            "company_name": contract['customer_info'].get('company_name'),
            "industry": contract['metrics']['industry'],
            "tier": contract['metrics']['tier'],
            "total_value": contract['metrics']['total_value'],
            "signed_date": contract['timestamp'].strftime('%Y-%m-%d'),
            "term_months": contract['metrics']['term_months']
        } for contract in sorted_contracts[:limit]] 