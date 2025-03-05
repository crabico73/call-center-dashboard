from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import uuid

class AmendmentType(Enum):
    SUBSCRIPTION_CHANGE = "subscription_change"
    TERM_EXTENSION = "term_extension"
    SLA_MODIFICATION = "sla_modification"
    COMPLIANCE_UPDATE = "compliance_update"
    USAGE_EXPANSION = "usage_expansion"
    PRICE_ADJUSTMENT = "price_adjustment"
    TERRITORY_EXPANSION = "territory_expansion"
    EXCLUSIVITY_MODIFICATION = "exclusivity_modification"

class AmendmentStatus(Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"

@dataclass
class AmendmentVersion:
    version_id: str
    created_at: datetime
    created_by: str
    changes: Dict[str, Any]
    comments: str
    status: AmendmentStatus

@dataclass
class AmendmentTemplate:
    name: str
    description: str
    required_approvals: List[str]
    notice_period: int  # days
    documentation_requirements: List[str]
    legal_review_required: bool

class ContractAmendmentService:
    def __init__(self):
        self.amendment_templates = {
            AmendmentType.SUBSCRIPTION_CHANGE: AmendmentTemplate(
                name="Subscription Plan Modification",
                description="Change in subscription tier or service level",
                required_approvals=["Sales", "Finance"],
                notice_period=30,
                documentation_requirements=[
                    "Current usage metrics",
                    "New plan details",
                    "Price impact analysis"
                ],
                legal_review_required=False
            ),
            AmendmentType.TERM_EXTENSION: AmendmentTemplate(
                name="Contract Term Extension",
                description="Extension of contract duration",
                required_approvals=["Sales", "Finance", "Legal"],
                notice_period=60,
                documentation_requirements=[
                    "Performance history",
                    "Updated pricing terms",
                    "Extension rationale"
                ],
                legal_review_required=True
            ),
            AmendmentType.SLA_MODIFICATION: AmendmentTemplate(
                name="Service Level Agreement Update",
                description="Modification of service level terms",
                required_approvals=["Operations", "Legal"],
                notice_period=45,
                documentation_requirements=[
                    "Current SLA performance",
                    "Proposed changes",
                    "Impact analysis"
                ],
                legal_review_required=True
            ),
            AmendmentType.COMPLIANCE_UPDATE: AmendmentTemplate(
                name="Compliance Requirement Update",
                description="Updates to compliance and regulatory terms",
                required_approvals=["Legal", "Compliance", "Security"],
                notice_period=30,
                documentation_requirements=[
                    "Regulatory requirements",
                    "Implementation timeline",
                    "Compliance certificates"
                ],
                legal_review_required=True
            ),
            AmendmentType.USAGE_EXPANSION: AmendmentTemplate(
                name="Usage Terms Expansion",
                description="Expansion of authorized usage scope",
                required_approvals=["Sales", "Operations"],
                notice_period=30,
                documentation_requirements=[
                    "Current usage patterns",
                    "Proposed expansion scope",
                    "Technical requirements"
                ],
                legal_review_required=False
            ),
            AmendmentType.PRICE_ADJUSTMENT: AmendmentTemplate(
                name="Price Terms Modification",
                description="Adjustment to pricing terms",
                required_approvals=["Sales", "Finance", "Legal"],
                notice_period=60,
                documentation_requirements=[
                    "Market analysis",
                    "Cost justification",
                    "Impact assessment"
                ],
                legal_review_required=True
            ),
            AmendmentType.TERRITORY_EXPANSION: AmendmentTemplate(
                name="Territory Coverage Extension",
                description="Expansion of geographic coverage",
                required_approvals=["Sales", "Operations", "Legal"],
                notice_period=45,
                documentation_requirements=[
                    "Market analysis",
                    "Operational capability assessment",
                    "Regulatory compliance verification"
                ],
                legal_review_required=True
            ),
            AmendmentType.EXCLUSIVITY_MODIFICATION: AmendmentTemplate(
                name="Exclusivity Terms Modification",
                description="Changes to exclusivity arrangements",
                required_approvals=["Sales", "Legal", "Executive"],
                notice_period=90,
                documentation_requirements=[
                    "Market impact analysis",
                    "Competition assessment",
                    "Value proposition"
                ],
                legal_review_required=True
            )
        }

        # Extended industry requirements
        self.industry_requirements = {
            "FINANCIAL": {
                "additional_approvers": ["Risk Management", "Compliance"],
                "extended_notice_periods": {
                    AmendmentType.COMPLIANCE_UPDATE: 45,
                    AmendmentType.SLA_MODIFICATION: 60
                },
                "additional_documentation": {
                    AmendmentType.COMPLIANCE_UPDATE: [
                        "SOC 2 compliance impact",
                        "Data security assessment"
                    ],
                    AmendmentType.USAGE_EXPANSION: [
                        "Transaction monitoring impact",
                        "Regulatory compliance assessment"
                    ]
                }
            },
            "HEALTHCARE": {
                "additional_approvers": ["Privacy Officer", "Medical Compliance"],
                "extended_notice_periods": {
                    AmendmentType.COMPLIANCE_UPDATE: 60,
                    AmendmentType.USAGE_EXPANSION: 45
                },
                "additional_documentation": {
                    AmendmentType.COMPLIANCE_UPDATE: [
                        "HIPAA compliance assessment",
                        "PHI handling procedures"
                    ],
                    AmendmentType.USAGE_EXPANSION: [
                        "Patient data impact analysis",
                        "Privacy impact assessment"
                    ]
                }
            },
            "RETAIL": {
                "additional_approvers": ["Operations Manager"],
                "extended_notice_periods": {
                    AmendmentType.USAGE_EXPANSION: 30,
                    AmendmentType.TERRITORY_EXPANSION: 45
                },
                "additional_documentation": {
                    AmendmentType.USAGE_EXPANSION: [
                        "Peak season capacity analysis",
                        "Multi-location deployment plan"
                    ],
                    AmendmentType.TERRITORY_EXPANSION: [
                        "Market analysis per location",
                        "Store integration timeline"
                    ]
                }
            },
            "MANUFACTURING": {
                "additional_approvers": ["Production Manager", "Quality Control"],
                "extended_notice_periods": {
                    AmendmentType.SLA_MODIFICATION: 45,
                    AmendmentType.COMPLIANCE_UPDATE: 30
                },
                "additional_documentation": {
                    AmendmentType.SLA_MODIFICATION: [
                        "Production impact analysis",
                        "Quality assurance metrics"
                    ],
                    AmendmentType.COMPLIANCE_UPDATE: [
                        "ISO compliance assessment",
                        "Safety protocol updates"
                    ]
                }
            },
            "EDUCATION": {
                "additional_approvers": ["Academic Affairs", "Student Services"],
                "extended_notice_periods": {
                    AmendmentType.USAGE_EXPANSION: 60,
                    AmendmentType.COMPLIANCE_UPDATE: 45
                },
                "additional_documentation": {
                    AmendmentType.USAGE_EXPANSION: [
                        "Student privacy impact",
                        "Academic calendar alignment"
                    ],
                    AmendmentType.COMPLIANCE_UPDATE: [
                        "FERPA compliance assessment",
                        "Accessibility requirements"
                    ]
                }
            }
        }

        # Version history storage
        self.amendment_versions: Dict[str, List[AmendmentVersion]] = {}
        
        # Workflow configurations
        self.workflow_configurations = {
            "parallel_approval_groups": {
                "standard": [
                    ["Sales", "Operations"],
                    ["Finance", "Compliance"]
                ],
                "high_value": [
                    ["Sales", "Operations", "Finance"],
                    ["Legal", "Compliance", "Risk Management"]
                ],
                "executive": [
                    ["CEO", "CFO"],
                    ["Legal", "Board"]
                ]
            },
            "approval_deadlines": {
                "standard": 5,
                "urgent": 2,
                "extended": 10
            },
            "escalation_rules": {
                "first_reminder": 48,  # hours
                "second_reminder": 72,  # hours
                "auto_escalation": 96   # hours
            }
        }

    def generate_amendment(self,
                         amendment_type: AmendmentType,
                         industry: str,
                         current_contract: Dict[str, Any],
                         amendment_details: Dict[str, Any],
                         created_by: str) -> Dict[str, Any]:
        """Generate an amendment template with industry-specific modifications"""
        
        # Generate base amendment
        amendment = super().generate_amendment(
            amendment_type,
            industry,
            current_contract,
            amendment_details
        )
        
        # Add version tracking
        version_id = str(uuid.uuid4())
        amendment["version"] = {
            "id": version_id,
            "number": "1.0",
            "created_at": datetime.now().isoformat(),
            "created_by": created_by,
            "status": AmendmentStatus.DRAFT.value
        }
        
        # Store initial version
        self._store_version(
            amendment["metadata"]["amendment_id"],
            AmendmentVersion(
                version_id=version_id,
                created_at=datetime.now(),
                created_by=created_by,
                changes=amendment_details,
                comments="Initial version",
                status=AmendmentStatus.DRAFT
            )
        )
        
        # Enhanced workflow based on amendment value and type
        self._enhance_workflow(amendment, amendment_details)
        
        return amendment

    def update_amendment(self,
                        amendment_id: str,
                        changes: Dict[str, Any],
                        updated_by: str,
                        comments: str) -> Dict[str, Any]:
        """Update an existing amendment with version tracking"""
        
        # Get latest version
        current_version = self._get_latest_version(amendment_id)
        if not current_version:
            raise ValueError("Amendment not found")
        
        # Create new version
        new_version_id = str(uuid.uuid4())
        new_version_number = self._increment_version(
            current_version.version_id
        )
        
        # Store new version
        new_version = AmendmentVersion(
            version_id=new_version_id,
            created_at=datetime.now(),
            created_by=updated_by,
            changes=changes,
            comments=comments,
            status=AmendmentStatus.DRAFT
        )
        
        self._store_version(amendment_id, new_version)
        
        return {
            "amendment_id": amendment_id,
            "version_id": new_version_id,
            "version_number": new_version_number,
            "updated_at": datetime.now().isoformat(),
            "updated_by": updated_by,
            "status": AmendmentStatus.DRAFT.value
        }

    def get_amendment_history(self, amendment_id: str) -> List[Dict[str, Any]]:
        """Retrieve version history for an amendment"""
        versions = self.amendment_versions.get(amendment_id, [])
        return [
            {
                "version_id": v.version_id,
                "created_at": v.created_at.isoformat(),
                "created_by": v.created_by,
                "comments": v.comments,
                "status": v.status.value
            }
            for v in versions
        ]

    def _store_version(self, amendment_id: str, version: AmendmentVersion):
        """Store a new version in the history"""
        if amendment_id not in self.amendment_versions:
            self.amendment_versions[amendment_id] = []
        self.amendment_versions[amendment_id].append(version)

    def _get_latest_version(self, amendment_id: str) -> Optional[AmendmentVersion]:
        """Get the latest version of an amendment"""
        versions = self.amendment_versions.get(amendment_id, [])
        return versions[-1] if versions else None

    def _increment_version(self, current_version: str) -> str:
        """Increment the version number"""
        major, minor = map(int, current_version.split('.'))
        return f"{major}.{minor + 1}"

    def _enhance_workflow(self, amendment: Dict[str, Any], details: Dict[str, Any]):
        """Enhance workflow based on amendment characteristics"""
        
        # Determine workflow type based on value
        value = details.get('value', 0)
        if value > 1000000:  # High-value deals
            approval_groups = self.workflow_configurations["parallel_approval_groups"]["high_value"]
            deadline = self.workflow_configurations["approval_deadlines"]["extended"]
        elif value > 500000:  # Medium-value deals
            approval_groups = self.workflow_configurations["parallel_approval_groups"]["standard"]
            deadline = self.workflow_configurations["approval_deadlines"]["standard"]
        else:  # Standard deals
            approval_groups = self.workflow_configurations["parallel_approval_groups"]["standard"]
            deadline = self.workflow_configurations["approval_deadlines"]["standard"]

        # Update workflow configuration
        amendment["approval_workflow"].update({
            "parallel_approval_groups": approval_groups,
            "approval_deadline_days": deadline,
            "escalation_rules": self.workflow_configurations["escalation_rules"],
            "approval_chain": self._generate_approval_chain(approval_groups)
        })

    def _generate_approval_chain(self, approval_groups: List[List[str]]) -> List[Dict[str, Any]]:
        """Generate a structured approval chain"""
        chain = []
        for group_index, group in enumerate(approval_groups):
            chain.append({
                "stage": group_index + 1,
                "approvers": group,
                "status": "pending",
                "requires_all": True,
                "approvals_received": [],
                "comments": []
            })
        return chain 