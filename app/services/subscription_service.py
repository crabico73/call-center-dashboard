from typing import Dict, Any, List
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
import math

class ExclusivityLevel(Enum):
    NONE = "none"
    CITY = "city"
    STATE = "state"
    REGION = "region"
    COUNTRY = "country"
    GLOBAL = "global"

class EnterpriseLicense(Enum):
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class Industry(Enum):
    FINANCIAL = "financial"
    HEALTHCARE = "healthcare"
    REAL_ESTATE = "real_estate"
    TECHNOLOGY = "technology"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    PROFESSIONAL_SERVICES = "professional_services"

@dataclass
class ExclusivityTerms:
    level: ExclusivityLevel
    territory: str
    duration_months: int
    monthly_fee: Decimal

@dataclass
class SubscriptionTier:
    name: str
    max_calls: int
    price_per_month: Decimal
    setup_fee: Decimal
    features: List[str]
    min_term_months: int
    overage_rate: Decimal

@dataclass
class EnterpriseLicenseTerms:
    license_type: EnterpriseLicense
    base_fee: Decimal
    max_locations: int
    max_total_calls: int
    features: List[str]
    support_level: str
    custom_development_hours: int

@dataclass
class MarketMetrics:
    total_addressable_market: float  # in millions
    market_growth_rate: float  # annual growth rate
    competition_intensity: float  # 0-1 scale
    average_deal_size: float
    customer_acquisition_cost: float
    market_maturity: float  # 0-1 scale

@dataclass
class IndustryProfile:
    name: Industry
    price_multiplier: float
    compliance_requirements: List[str]
    average_call_duration: int  # in seconds
    peak_hours: List[int]
    specialized_features: List[str]
    cost_multiplier: float

class SubscriptionService:
    def __init__(self):
        # Standard Subscription Tiers
        self.subscription_tiers = {
            "starter": SubscriptionTier(
                name="Starter",
                max_calls=1000,
                price_per_month=Decimal("450"),
                setup_fee=Decimal("1000"),
                features=[
                    "AI-powered outbound calls",
                    "Basic analytics dashboard",
                    "Standard business hours support",
                    "Basic call scripts"
                ],
                min_term_months=6,
                overage_rate=Decimal("0.50")
            ),
            "professional": SubscriptionTier(
                name="Professional",
                max_calls=5000,
                price_per_month=Decimal("2000"),
                setup_fee=Decimal("2500"),
                features=[
                    "All Starter features",
                    "24/7 call availability",
                    "Advanced analytics and reporting",
                    "Custom call scripts",
                    "Priority support",
                    "Call recording and transcription"
                ],
                min_term_months=12,
                overage_rate=Decimal("0.45")
            ),
            "enterprise": SubscriptionTier(
                name="Enterprise",
                max_calls=10000,
                price_per_month=Decimal("3500"),
                setup_fee=Decimal("5000"),
                features=[
                    "All Professional features",
                    "Dedicated account manager",
                    "Custom AI agent personalities",
                    "API integration",
                    "Advanced customization options",
                    "SLA guarantees",
                    "Training and onboarding support"
                ],
                min_term_months=12,
                overage_rate=Decimal("0.40")
            ),
            "ultimate": SubscriptionTier(
                name="Ultimate",
                max_calls=25000,
                price_per_month=Decimal("7500"),
                setup_fee=Decimal("10000"),
                features=[
                    "All Enterprise features",
                    "Multi-language support",
                    "Custom integration development",
                    "Dedicated development team",
                    "White-label options",
                    "Custom analytics development",
                    "Executive quarterly reviews"
                ],
                min_term_months=24,
                overage_rate=Decimal("0.35")
            )
        }

        # Enterprise License Tiers
        self.enterprise_licenses = {
            "silver": EnterpriseLicenseTerms(
                license_type=EnterpriseLicense.SILVER,
                base_fee=Decimal("25000"),
                max_locations=3,
                max_total_calls=50000,
                features=[
                    "All Ultimate tier features",
                    "Multi-location deployment",
                    "Centralized management console",
                    "Enhanced SLA guarantees",
                    "Quarterly business reviews"
                ],
                support_level="Premium",
                custom_development_hours=20
            ),
            "gold": EnterpriseLicenseTerms(
                license_type=EnterpriseLicense.GOLD,
                base_fee=Decimal("50000"),
                max_locations=10,
                max_total_calls=150000,
                features=[
                    "All Silver license features",
                    "Priority feature development",
                    "Custom AI model training",
                    "Advanced integration options",
                    "24/7 dedicated support team"
                ],
                support_level="Enterprise",
                custom_development_hours=50
            ),
            "platinum": EnterpriseLicenseTerms(
                license_type=EnterpriseLicense.PLATINUM,
                base_fee=Decimal("100000"),
                max_locations=999999,  # Unlimited
                max_total_calls=999999,  # Unlimited
                features=[
                    "All Gold license features",
                    "Unlimited locations",
                    "Unlimited calls",
                    "Custom feature development",
                    "Source code access",
                    "Technology partnership status"
                ],
                support_level="Executive",
                custom_development_hours=100
            )
        }

        # Exclusivity Pricing
        self.exclusivity_base_rates = {
            ExclusivityLevel.CITY: Decimal("5000"),
            ExclusivityLevel.STATE: Decimal("25000"),
            ExclusivityLevel.REGION: Decimal("75000"),
            ExclusivityLevel.COUNTRY: Decimal("150000"),
            ExclusivityLevel.GLOBAL: Decimal("500000")
        }

        # Add industry profiles
        self.industry_profiles = {
            Industry.FINANCIAL: IndustryProfile(
                name=Industry.FINANCIAL,
                price_multiplier=1.3,
                compliance_requirements=["SEC", "FINRA", "BSA/AML", "KYC"],
                average_call_duration=420,
                peak_hours=[9, 10, 11, 14, 15],
                specialized_features=[
                    "Compliance recording",
                    "Risk assessment",
                    "Fraud detection",
                    "Transaction verification"
                ],
                cost_multiplier=1.4
            ),
            Industry.HEALTHCARE: IndustryProfile(
                name=Industry.HEALTHCARE,
                price_multiplier=1.25,
                compliance_requirements=["HIPAA", "HITECH", "PHI Protection"],
                average_call_duration=360,
                peak_hours=[8, 9, 10, 14, 15, 16],
                specialized_features=[
                    "PHI handling",
                    "Medical terminology",
                    "Insurance verification",
                    "Appointment scheduling"
                ],
                cost_multiplier=1.35
            ),
            Industry.REAL_ESTATE: IndustryProfile(
                name=Industry.REAL_ESTATE,
                price_multiplier=1.1,
                compliance_requirements=["Fair Housing", "RESPA"],
                average_call_duration=300,
                peak_hours=[10, 11, 12, 14, 15, 16, 17],
                specialized_features=[
                    "Property matching",
                    "Scheduling viewings",
                    "Market analysis",
                    "Lead scoring"
                ],
                cost_multiplier=1.15
            ),
            Industry.TECHNOLOGY: IndustryProfile(
                name=Industry.TECHNOLOGY,
                price_multiplier=1.2,
                compliance_requirements=["Data Protection", "GDPR", "CCPA"],
                average_call_duration=480,
                peak_hours=[9, 10, 11, 13, 14, 15, 16],
                specialized_features=[
                    "Technical qualification",
                    "Product compatibility",
                    "Integration planning",
                    "Technical support"
                ],
                cost_multiplier=1.25
            )
        }

        # Volume discount tiers
        self.volume_discounts = [
            (50000, 0.05),   # 5% discount for 50k+ calls
            (100000, 0.10),  # 10% discount for 100k+ calls
            (250000, 0.15),  # 15% discount for 250k+ calls
            (500000, 0.20),  # 20% discount for 500k+ calls
            (1000000, 0.25)  # 25% discount for 1M+ calls
        ]

        # Contract term incentives
        self.term_incentives = [
            (12, 0.00),  # No discount for 1 year
            (24, 0.10),  # 10% discount for 2 years
            (36, 0.15),  # 15% discount for 3 years
            (48, 0.20),  # 20% discount for 4 years
            (60, 0.25)   # 25% discount for 5 years
        ]

        # Add market metrics templates
        self.market_metrics_templates = {
            Industry.FINANCIAL: MarketMetrics(
                total_addressable_market=500.0,
                market_growth_rate=0.12,
                competition_intensity=0.8,
                average_deal_size=75000.0,
                customer_acquisition_cost=15000.0,
                market_maturity=0.7
            ),
            Industry.HEALTHCARE: MarketMetrics(
                total_addressable_market=800.0,
                market_growth_rate=0.15,
                competition_intensity=0.6,
                average_deal_size=60000.0,
                customer_acquisition_cost=12000.0,
                market_maturity=0.5
            ),
            Industry.REAL_ESTATE: MarketMetrics(
                total_addressable_market=300.0,
                market_growth_rate=0.08,
                competition_intensity=0.7,
                average_deal_size=45000.0,
                customer_acquisition_cost=9000.0,
                market_maturity=0.8
            ),
            Industry.TECHNOLOGY: MarketMetrics(
                total_addressable_market=600.0,
                market_growth_rate=0.18,
                competition_intensity=0.9,
                average_deal_size=90000.0,
                customer_acquisition_cost=18000.0,
                market_maturity=0.6
            )
        }

    def calculate_subscription_cost(self,
                                 tier_name: str,
                                 duration_months: int,
                                 estimated_calls: int) -> Dict[str, Any]:
        """Calculate total subscription cost including potential overages"""
        tier = self.subscription_tiers.get(tier_name.lower())
        if not tier:
            raise ValueError(f"Invalid tier: {tier_name}")

        if duration_months < tier.min_term_months:
            raise ValueError(f"Minimum term for {tier_name} is {tier.min_term_months} months")

        base_monthly = float(tier.price_per_month)
        setup = float(tier.setup_fee)
        
        # Calculate potential overage
        monthly_overage = max(0, estimated_calls - tier.max_calls)
        overage_cost = float(monthly_overage * tier.overage_rate)

        return {
            "base_monthly_fee": base_monthly,
            "setup_fee": setup,
            "estimated_monthly_overage": overage_cost,
            "total_monthly_cost": base_monthly + overage_cost,
            "total_contract_value": (base_monthly + overage_cost) * duration_months + setup
        }

    def calculate_enterprise_license_cost(self,
                                       license_type: str,
                                       num_locations: int,
                                       estimated_total_calls: int) -> Dict[str, Any]:
        """Calculate enterprise license costs"""
        license_terms = self.enterprise_licenses.get(license_type.lower())
        if not license_terms:
            raise ValueError(f"Invalid license type: {license_type}")

        if num_locations > license_terms.max_locations:
            raise ValueError(f"Number of locations exceeds {license_type} license maximum")

        if estimated_total_calls > license_terms.max_total_calls:
            raise ValueError(f"Estimated calls exceed {license_type} license maximum")

        return {
            "monthly_base_fee": float(license_terms.base_fee),
            "included_locations": license_terms.max_locations,
            "included_calls": license_terms.max_total_calls,
            "support_level": license_terms.support_level,
            "custom_dev_hours": license_terms.custom_development_hours,
            "features": license_terms.features
        }

    def calculate_exclusivity_cost(self,
                                 level: str,
                                 territory: str,
                                 duration_months: int,
                                 market_size: float) -> Dict[str, Any]:
        """Calculate exclusivity costs based on territory and market size"""
        try:
            exclusivity_level = ExclusivityLevel[level.upper()]
        except KeyError:
            raise ValueError(f"Invalid exclusivity level: {level}")

        base_rate = float(self.exclusivity_base_rates[exclusivity_level])
        
        # Adjust based on market size and duration
        market_multiplier = market_size / 1000000  # per million in market size
        duration_multiplier = max(1, duration_months / 12)
        
        monthly_fee = base_rate * market_multiplier * duration_multiplier

        return {
            "level": exclusivity_level.value,
            "territory": territory,
            "duration_months": duration_months,
            "monthly_fee": round(monthly_fee, 2),
            "total_cost": round(monthly_fee * duration_months, 2)
        }

    def calculate_buyout_value(self,
                             current_contract_value: float,
                             monthly_recurring_revenue: float,
                             market_penetration: float,
                             remaining_term_months: int) -> Dict[str, Any]:
        """Calculate buyout value for market expansion"""
        # Base multiplier on remaining term
        term_multiplier = max(1, remaining_term_months / 12)
        
        # Revenue multiple based on market penetration
        revenue_multiple = 4.0 + (market_penetration * 2)  # 4x to 6x multiple
        
        # Calculate components
        remaining_contract = current_contract_value * (remaining_term_months / 12)
        future_value = monthly_recurring_revenue * 12 * revenue_multiple
        
        buyout_value = (remaining_contract + future_value) * term_multiplier

        return {
            "base_contract_value": round(remaining_contract, 2),
            "future_value": round(future_value, 2),
            "term_multiplier": round(term_multiplier, 2),
            "revenue_multiple": round(revenue_multiple, 2),
            "total_buyout_value": round(buyout_value, 2)
        }

    def calculate_market_size(self,
                            industry: str,
                            region: str,
                            target_companies: int,
                            avg_company_size: float) -> Dict[str, Any]:
        """Calculate detailed market size and opportunity"""
        try:
            industry_enum = Industry[industry.upper()]
            base_metrics = self.market_metrics_templates[industry_enum]
        except KeyError:
            raise ValueError(f"Invalid industry: {industry}")

        # Calculate total opportunity
        market_size = target_companies * avg_company_size
        
        # Adjust for industry factors
        industry_profile = self.industry_profiles[industry_enum]
        adjusted_market = market_size * industry_profile.cost_multiplier
        
        # Calculate penetration potential
        penetration_rate = self._calculate_penetration_rate(
            base_metrics.market_maturity,
            base_metrics.competition_intensity
        )
        
        # Project growth
        year_1_potential = adjusted_market * penetration_rate
        year_3_potential = year_1_potential * (1 + base_metrics.market_growth_rate) ** 3
        year_5_potential = year_1_potential * (1 + base_metrics.market_growth_rate) ** 5

        return {
            "total_market_size": round(adjusted_market, 2),
            "serviceable_market": round(adjusted_market * penetration_rate, 2),
            "year_1_potential": round(year_1_potential, 2),
            "year_3_potential": round(year_3_potential, 2),
            "year_5_potential": round(year_5_potential, 2),
            "metrics": {
                "growth_rate": base_metrics.market_growth_rate,
                "competition_intensity": base_metrics.competition_intensity,
                "market_maturity": base_metrics.market_maturity,
                "penetration_rate": penetration_rate
            }
        }

    def calculate_industry_adjusted_pricing(self,
                                         base_price: Decimal,
                                         industry: str,
                                         call_complexity: float = 1.0) -> Dict[str, Any]:
        """Calculate industry-specific pricing adjustments"""
        try:
            industry_enum = Industry[industry.upper()]
            profile = self.industry_profiles[industry_enum]
        except KeyError:
            raise ValueError(f"Invalid industry: {industry}")

        # Base adjustment
        industry_multiplier = profile.price_multiplier
        
        # Complexity adjustment
        complexity_multiplier = 1.0 + (call_complexity - 1.0) * 0.2
        
        # Compliance cost
        compliance_cost = len(profile.compliance_requirements) * 100  # $100 per requirement
        
        # Feature premium
        feature_premium = len(profile.specialized_features) * 50  # $50 per feature
        
        adjusted_price = float(base_price) * industry_multiplier * complexity_multiplier
        
        return {
            "base_price": float(base_price),
            "adjusted_price": round(adjusted_price, 2),
            "industry_multiplier": industry_multiplier,
            "complexity_multiplier": complexity_multiplier,
            "compliance_cost": compliance_cost,
            "feature_premium": feature_premium,
            "total_monthly_premium": round(compliance_cost + feature_premium, 2),
            "specialized_features": profile.specialized_features,
            "compliance_requirements": profile.compliance_requirements
        }

    def calculate_volume_discounts(self,
                                 base_price: Decimal,
                                 annual_call_volume: int,
                                 contract_months: int) -> Dict[str, Any]:
        """Calculate volume-based discounts"""
        # Find applicable volume discount
        volume_discount = 0.0
        for threshold, discount in self.volume_discounts:
            if annual_call_volume >= threshold:
                volume_discount = discount
                break
        
        # Find applicable term discount
        term_discount = 0.0
        for months, discount in self.term_incentives:
            if contract_months >= months:
                term_discount = discount
                break
        
        # Calculate combined discount
        combined_discount = 1 - ((1 - volume_discount) * (1 - term_discount))
        
        # Calculate savings
        base_annual = float(base_price) * 12
        discounted_annual = base_annual * (1 - combined_discount)
        
        return {
            "base_annual_price": base_annual,
            "discounted_annual_price": round(discounted_annual, 2),
            "volume_discount": volume_discount,
            "term_discount": term_discount,
            "combined_discount": combined_discount,
            "annual_savings": round(base_annual - discounted_annual, 2),
            "total_contract_savings": round((base_annual - discounted_annual) * 
                                         (contract_months / 12), 2)
        }

    def optimize_contract_terms(self,
                              estimated_calls: int,
                              industry: str,
                              budget_constraint: float = None) -> Dict[str, Any]:
        """Optimize contract terms for maximum value"""
        try:
            industry_enum = Industry[industry.upper()]
            profile = self.industry_profiles[industry_enum]
        except KeyError:
            raise ValueError(f"Invalid industry: {industry}")

        # Find optimal tier
        optimal_tier = None
        optimal_term = 12
        min_cost = float('inf')
        best_value = 0
        
        for tier_name, tier in self.subscription_tiers.items():
            for term_months, term_discount in self.term_incentives:
                # Calculate costs with volume and term discounts
                volume_discounts = self.calculate_volume_discounts(
                    tier.price_per_month,
                    estimated_calls * 12,
                    term_months
                )
                
                monthly_cost = float(tier.price_per_month) * (1 - volume_discounts["combined_discount"])
                total_cost = monthly_cost * term_months + float(tier.setup_fee)
                
                # Calculate value score
                value_score = self._calculate_value_score(
                    tier,
                    term_months,
                    estimated_calls,
                    profile,
                    monthly_cost
                )
                
                # Check budget constraint
                if budget_constraint and total_cost > budget_constraint:
                    continue
                
                # Update optimal if better value found
                if value_score > best_value or (value_score == best_value and total_cost < min_cost):
                    optimal_tier = tier
                    optimal_term = term_months
                    min_cost = total_cost
                    best_value = value_score

        if not optimal_tier:
            return {"error": "No suitable configuration found within constraints"}

        # Calculate optimized costs
        optimized_costs = self.calculate_subscription_cost(
            optimal_tier.name,
            optimal_term,
            estimated_calls
        )
        
        return {
            "recommended_tier": optimal_tier.name,
            "recommended_term": optimal_term,
            "monthly_cost": round(min_cost / optimal_term, 2),
            "total_contract_value": round(min_cost, 2),
            "value_score": round(best_value, 2),
            "cost_breakdown": optimized_costs,
            "features": optimal_tier.features,
            "roi_period_months": self._calculate_roi_period(
                min_cost,
                estimated_calls,
                profile
            )
        }

    def _calculate_penetration_rate(self,
                                  market_maturity: float,
                                  competition_intensity: float) -> float:
        """Calculate expected market penetration rate"""
        base_rate = 0.3  # 30% base penetration
        maturity_factor = 1 - (market_maturity * 0.5)  # Harder to penetrate mature markets
        competition_factor = 1 - (competition_intensity * 0.7)  # Harder with more competition
        
        return base_rate * maturity_factor * competition_factor

    def _calculate_value_score(self,
                             tier: SubscriptionTier,
                             term_months: int,
                             estimated_calls: int,
                             industry_profile: IndustryProfile,
                             monthly_cost: float) -> float:
        """Calculate value score for optimization"""
        feature_value = len(tier.features) * 10
        term_value = math.log(term_months) * 5
        volume_efficiency = min(1.0, tier.max_calls / estimated_calls) * 20
        industry_alignment = sum(1 for f in tier.features 
                               if f in industry_profile.specialized_features) * 15
        cost_efficiency = (1000 / monthly_cost) * 10  # Inverse cost factor
        
        return feature_value + term_value + volume_efficiency + industry_alignment + cost_efficiency

    def _calculate_roi_period(self,
                            total_cost: float,
                            estimated_calls: int,
                            industry_profile: IndustryProfile) -> int:
        """Calculate expected ROI period in months"""
        monthly_calls = estimated_calls
        cost_per_human_call = 8.0 * industry_profile.cost_multiplier
        monthly_savings = monthly_calls * (cost_per_human_call - 0.5)  # $0.50 is our cost
        
        return math.ceil(total_cost / monthly_savings) 