"""
Fynix Systems - Compliance Agent
================================
Automated compliance monitoring for contractor-specific regulations.

Blue Ocean Differentiator: Generic bookkeeping ignores compliance.
This agent proactively monitors:
- License renewals
- Insurance expirations
- Workers comp audits
- Tax filing deadlines
- Trade-specific regulations (EPA 608 for HVAC, etc.)
- Contractor licensing requirements by state
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

from agents.orchestrator import BaseAgent, Task, ClientProfile, AgentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ComplianceAgent")


class ComplianceType(Enum):
    LICENSE = "license"
    INSURANCE = "insurance"
    TAX = "tax"
    CERTIFICATION = "certification"
    PERMIT = "permit"
    AUDIT = "audit"
    REGISTRATION = "registration"


class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    COMPLIANT = "compliant"


@dataclass
class ComplianceItem:
    """A compliance requirement being tracked."""
    item_id: str
    name: str
    compliance_type: ComplianceType
    description: str
    due_date: Optional[datetime]
    last_completed: Optional[datetime]
    status: RiskLevel
    action_required: str
    estimated_cost: Optional[float] = None
    renewal_period_months: int = 12
    trade_specific: Optional[str] = None
    state_specific: Optional[str] = None
    notes: str = ""


class ComplianceAgent(BaseAgent):
    """
    Compliance Agent - Never miss a deadline, never be out of compliance.
    """
    
    def __init__(self):
        super().__init__(AgentType.COMPLIANCE)
        self.compliance_database = self._load_compliance_requirements()
        
    async def process(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """Process compliance-related tasks."""
        action = task.payload.get("action", "check_status")
        
        action_handlers = {
            "check_status": self._check_compliance_status,
            "generate_calendar": self._generate_compliance_calendar,
            "workers_comp_audit": self._prepare_workers_comp_audit,
            "insurance_certificates": self._manage_insurance_certificates,
            "tax_deadlines": self._get_tax_deadlines,
            "license_status": self._check_license_status,
        }
        
        handler = action_handlers.get(action, self._check_compliance_status)
        return await handler(task, client)
        
    async def _check_compliance_status(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """Comprehensive compliance status check."""
        
        items = self._get_applicable_requirements(client)
        
        critical = [i for i in items if i.status == RiskLevel.CRITICAL]
        high = [i for i in items if i.status == RiskLevel.HIGH]
        medium = [i for i in items if i.status == RiskLevel.MEDIUM]
        low = [i for i in items if i.status == RiskLevel.LOW]
        compliant = [i for i in items if i.status == RiskLevel.COMPLIANT]
        
        return {
            "status": "complete",
            "client": client.business_name,
            "checked_at": datetime.now().isoformat(),
            
            "summary": {
                "total_items": len(items),
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low),
                "compliant": len(compliant),
                "overall_status": self._calculate_overall_status(items)
            },
            
            "critical_items": [self._item_to_dict(i) for i in critical],
            "high_priority": [self._item_to_dict(i) for i in high],
            "upcoming": [self._item_to_dict(i) for i in medium + low],
            "compliant_items": [self._item_to_dict(i) for i in compliant],
            
            "recommended_actions": self._generate_action_items(critical + high),
            
            "next_check": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
    async def _generate_compliance_calendar(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        Generate annual compliance calendar.
        Shows all compliance events for the year with due dates.
        """
        
        items = self._get_applicable_requirements(client)
        
        # Organize by month
        calendar = {}
        for month in range(1, 13):
            month_name = datetime(2024, month, 1).strftime("%B")
            calendar[month_name] = []
            
        for item in items:
            if item.due_date:
                month_name = item.due_date.strftime("%B")
                if month_name in calendar:
                    calendar[month_name].append({
                        "name": item.name,
                        "due_date": item.due_date.strftime("%B %d"),
                        "type": item.compliance_type.value,
                        "cost": item.estimated_cost
                    })
                    
        return {
            "calendar_type": "annual_compliance",
            "client": client.business_name,
            "year": datetime.now().year,
            "generated_at": datetime.now().isoformat(),
            "calendar": calendar,
            "annual_compliance_cost_estimate": sum(
                i.estimated_cost or 0 for i in items
            )
        }
        
    async def _prepare_workers_comp_audit(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        Prepare for workers compensation audit.
        
        Workers comp audits are a pain point for contractors.
        This agent prepares all documentation automatically.
        """
        
        return {
            "audit_type": "workers_compensation",
            "client": client.business_name,
            "prepared_at": datetime.now().isoformat(),
            
            "required_documents": [
                {
                    "document": "Quarterly Payroll Reports",
                    "status": "available",
                    "location": "Payroll System Export"
                },
                {
                    "document": "941 Quarterly Tax Returns",
                    "status": "available",
                    "location": "Tax Documents"
                },
                {
                    "document": "Employee Classification Summary",
                    "status": "generated",
                    "data": {
                        "total_employees": 5,
                        "by_class": {
                            "5537": {"description": "HVAC Installation", "employees": 3, "payroll_ytd": 95000},
                            "8742": {"description": "Sales/Admin", "employees": 2, "payroll_ytd": 45000}
                        }
                    }
                },
                {
                    "document": "Subcontractor Certificates of Insurance",
                    "status": "3 of 5 on file",
                    "action_required": "Request updated COIs from 2 subs"
                },
                {
                    "document": "1099 Report",
                    "status": "available",
                    "total_1099_payments": 28500
                }
            ],
            
            "payroll_summary": {
                "gross_payroll_ytd": 140000,
                "by_quarter": {
                    "Q1": 32000,
                    "Q2": 38000,
                    "Q3": 42000,
                    "Q4_projected": 28000
                }
            },
            
            "subcontractor_summary": {
                "total_payments": 28500,
                "contractors_with_coi": 3,
                "contractors_needing_coi": 2,
                "uninsured_sub_exposure": 12000
            },
            
            "audit_tips": [
                "Ensure all subcontractors have current COIs on file",
                "Verify employee classifications match job duties",
                "Reconcile payroll to 941s before auditor arrives",
                "Prepare explanation for any overtime spikes",
                "Have breakdown of clerical vs. field payroll ready"
            ],
            
            "estimated_premium_adjustment": {
                "current_mod": 0.95,
                "experience_mod_expiration": "March 1, 2025",
                "estimated_audit_result": "Slight additional premium expected based on payroll growth"
            }
        }
        
    async def _manage_insurance_certificates(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        Insurance certificate management.
        Track all insurance policies and certificate requirements.
        """
        
        policies = [
            {
                "policy_type": "General Liability",
                "carrier": "State Farm",
                "policy_number": "GL-XXXXXX",
                "effective_date": "2024-03-01",
                "expiration_date": "2025-03-01",
                "coverage_amount": 1000000,
                "aggregate": 2000000,
                "status": "active",
                "days_until_renewal": 62
            },
            {
                "policy_type": "Workers Compensation",
                "carrier": "Liberty Mutual",
                "policy_number": "WC-XXXXXX",
                "effective_date": "2024-01-01",
                "expiration_date": "2025-01-01",
                "mod_rate": 0.95,
                "status": "active",
                "days_until_renewal": 3,
                "alert": "RENEWAL IMMINENT"
            },
            {
                "policy_type": "Commercial Auto",
                "carrier": "Progressive",
                "policy_number": "CA-XXXXXX",
                "effective_date": "2024-06-01",
                "expiration_date": "2025-06-01",
                "coverage_amount": 1000000,
                "status": "active",
                "days_until_renewal": 154
            },
            {
                "policy_type": "Umbrella/Excess",
                "carrier": "State Farm",
                "policy_number": "UM-XXXXXX",
                "effective_date": "2024-03-01",
                "expiration_date": "2025-03-01",
                "coverage_amount": 2000000,
                "status": "active",
                "days_until_renewal": 62
            }
        ]
        
        # Pending certificate requests
        pending_cois = [
            {
                "requested_by": "ABC Property Management",
                "requested_date": "2024-12-20",
                "required_coverages": ["GL", "WC", "Auto"],
                "additional_insured": True,
                "status": "pending",
                "days_outstanding": 8
            }
        ]
        
        return {
            "insurance_status": "review_needed",
            "client": client.business_name,
            "checked_at": datetime.now().isoformat(),
            
            "policies": policies,
            
            "alerts": [
                {
                    "type": "renewal",
                    "policy": "Workers Compensation",
                    "message": "Renews in 3 days - confirm renewal with Liberty Mutual",
                    "severity": "critical"
                }
            ],
            
            "pending_certificate_requests": pending_cois,
            
            "subcontractor_cois": {
                "total_subs_used": 5,
                "current_cois_on_file": 3,
                "expired_cois": 1,
                "missing_cois": 1,
                "action_required": [
                    "Request updated COI from Johnson Electric (expired 12/15)",
                    "Request COI from new sub: Martinez Plumbing"
                ]
            },
            
            "annual_insurance_cost": {
                "general_liability": 4200,
                "workers_comp": 8500,
                "commercial_auto": 6200,
                "umbrella": 1800,
                "total": 20700
            }
        }
        
    async def _get_tax_deadlines(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        Tax deadline tracking.
        All federal, state, and local tax obligations.
        """
        
        current_year = datetime.now().year
        
        # Federal deadlines (S-Corp example)
        federal_deadlines = [
            {
                "deadline": f"{current_year}-01-15",
                "description": "Q4 Estimated Tax Payment",
                "type": "payment",
                "status": "upcoming"
            },
            {
                "deadline": f"{current_year}-01-31",
                "description": "W-2s Due to Employees",
                "type": "filing",
                "status": "upcoming"
            },
            {
                "deadline": f"{current_year}-01-31",
                "description": "1099-NEC Filing Deadline",
                "type": "filing",
                "status": "upcoming"
            },
            {
                "deadline": f"{current_year}-03-15",
                "description": "S-Corp Tax Return (Form 1120S)",
                "type": "filing",
                "status": "upcoming"
            },
            {
                "deadline": f"{current_year}-04-15",
                "description": "Q1 Estimated Tax Payment",
                "type": "payment",
                "status": "upcoming"
            },
            {
                "deadline": f"{current_year}-04-15",
                "description": "Personal Tax Return (Form 1040)",
                "type": "filing",
                "status": "upcoming"
            }
        ]
        
        # State-specific (Georgia example)
        state_deadlines = [
            {
                "deadline": f"{current_year}-01-31",
                "description": "GA Withholding Annual Reconciliation (G-1003)",
                "type": "filing",
                "status": "upcoming"
            },
            {
                "deadline": f"{current_year}-03-15",
                "description": "GA S-Corp Return",
                "type": "filing",
                "status": "upcoming"
            },
            {
                "deadline": f"{current_year}-04-15",
                "description": "GA Individual Return",
                "type": "filing",
                "status": "upcoming"
            }
        ]
        
        # Recurring deadlines
        recurring = [
            {
                "frequency": "quarterly",
                "description": "Form 941 - Quarterly Payroll Tax",
                "due_dates": ["01/31", "04/30", "07/31", "10/31"]
            },
            {
                "frequency": "monthly",
                "description": "GA Sales Tax (if applicable)",
                "due_date": "20th of following month"
            }
        ]
        
        return {
            "tax_deadlines": "complete",
            "client": client.business_name,
            "tax_classification": client.tax_classification,
            "state": client.state,
            "generated_at": datetime.now().isoformat(),
            
            "upcoming_90_days": [
                d for d in federal_deadlines + state_deadlines
                if datetime.strptime(d["deadline"], "%Y-%m-%d") <= datetime.now() + timedelta(days=90)
            ],
            
            "federal_deadlines": federal_deadlines,
            "state_deadlines": state_deadlines,
            "recurring_obligations": recurring,
            
            "preparation_checklist": {
                "year_end": [
                    "Gather all 1099 contractor information",
                    "Verify W-2 data accuracy",
                    "Reconcile payroll to 941s",
                    "Review vehicle mileage logs",
                    "Compile equipment purchase list for depreciation",
                    "Gather home office expense documentation",
                    "Calculate retirement contribution amounts"
                ],
                "quarterly": [
                    "Prepare 941 data",
                    "Calculate estimated tax payment",
                    "Review YTD P&L for tax planning"
                ]
            }
        }
        
    async def _check_license_status(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        License and certification tracking.
        Trade-specific licenses, contractor licenses, etc.
        """
        
        licenses = {
            "HVAC": [
                {
                    "license_type": "State Contractor License",
                    "license_number": "HVAC-XXXXX",
                    "state": client.state,
                    "expiration": "2025-06-30",
                    "renewal_fee": 175,
                    "ce_required": 8,
                    "ce_completed": 4,
                    "status": "active"
                },
                {
                    "license_type": "EPA Section 608 Certification",
                    "certification_type": "Universal",
                    "holder": "Lead Technician",
                    "expiration": "N/A (Lifetime)",
                    "status": "active"
                },
                {
                    "license_type": "City Business License",
                    "city": "LaGrange",
                    "expiration": "2025-12-31",
                    "renewal_fee": 150,
                    "status": "active"
                }
            ],
            "Plumbing": [
                {
                    "license_type": "Master Plumber License",
                    "license_number": "MP-XXXXX",
                    "state": client.state,
                    "expiration": "2025-03-31",
                    "renewal_fee": 200,
                    "ce_required": 6,
                    "status": "active"
                },
                {
                    "license_type": "Backflow Certification",
                    "expiration": "2025-09-30",
                    "renewal_fee": 75,
                    "status": "active"
                }
            ]
        }
        
        trade_licenses = licenses.get(client.trade, [])
        
        return {
            "license_status": "complete",
            "client": client.business_name,
            "trade": client.trade,
            "state": client.state,
            "checked_at": datetime.now().isoformat(),
            
            "licenses": trade_licenses,
            
            "expiring_soon": [
                l for l in trade_licenses 
                if l.get("expiration") and l.get("expiration") != "N/A (Lifetime)"
                and datetime.strptime(l["expiration"], "%Y-%m-%d") <= datetime.now() + timedelta(days=90)
            ],
            
            "ce_status": {
                "required": sum(l.get("ce_required", 0) for l in trade_licenses),
                "completed": sum(l.get("ce_completed", 0) for l in trade_licenses),
                "remaining": sum(l.get("ce_required", 0) for l in trade_licenses) - 
                            sum(l.get("ce_completed", 0) for l in trade_licenses)
            },
            
            "renewal_costs_next_12mo": sum(
                l.get("renewal_fee", 0) for l in trade_licenses
            )
        }
        
    def _get_applicable_requirements(
        self, 
        client: ClientProfile
    ) -> List[ComplianceItem]:
        """Get all compliance requirements applicable to this client."""
        
        # Base items for all contractors
        items = [
            ComplianceItem(
                item_id="fed_tax_941",
                name="Quarterly Payroll Tax (Form 941)",
                compliance_type=ComplianceType.TAX,
                description="Federal payroll tax return",
                due_date=datetime(2025, 1, 31),
                last_completed=datetime(2024, 10, 31),
                status=RiskLevel.LOW,
                action_required="Prepare Q4 941",
                estimated_cost=0,
                renewal_period_months=3
            ),
            ComplianceItem(
                item_id="workers_comp",
                name="Workers Compensation Renewal",
                compliance_type=ComplianceType.INSURANCE,
                description="Annual WC policy renewal",
                due_date=datetime(2025, 1, 1),
                last_completed=datetime(2024, 1, 1),
                status=RiskLevel.CRITICAL,
                action_required="Renew workers comp policy - expires in 3 days",
                estimated_cost=8500
            ),
            ComplianceItem(
                item_id="general_liability",
                name="General Liability Insurance",
                compliance_type=ComplianceType.INSURANCE,
                description="Annual GL policy",
                due_date=datetime(2025, 3, 1),
                last_completed=datetime(2024, 3, 1),
                status=RiskLevel.MEDIUM,
                action_required="Begin renewal process",
                estimated_cost=4200
            ),
            ComplianceItem(
                item_id="business_license",
                name="City Business License",
                compliance_type=ComplianceType.LICENSE,
                description="Annual city business license renewal",
                due_date=datetime(2025, 12, 31),
                last_completed=datetime(2024, 1, 15),
                status=RiskLevel.COMPLIANT,
                action_required="None - current through year end",
                estimated_cost=150
            )
        ]
        
        # Add trade-specific items
        if client.trade == "HVAC":
            items.extend([
                ComplianceItem(
                    item_id="epa_608",
                    name="EPA 608 Certification Tracking",
                    compliance_type=ComplianceType.CERTIFICATION,
                    description="Ensure all technicians have valid EPA 608",
                    due_date=None,  # Lifetime certification
                    last_completed=None,
                    status=RiskLevel.COMPLIANT,
                    action_required="Verify certifications for any new hires",
                    trade_specific="HVAC"
                ),
                ComplianceItem(
                    item_id="refrigerant_tracking",
                    name="Refrigerant Purchase/Usage Log",
                    compliance_type=ComplianceType.REGISTRATION,
                    description="EPA requires tracking of refrigerant purchases and usage",
                    due_date=None,  # Ongoing
                    last_completed=datetime.now() - timedelta(days=7),
                    status=RiskLevel.COMPLIANT,
                    action_required="Maintain current logs",
                    trade_specific="HVAC"
                )
            ])
            
        elif client.trade == "Plumbing":
            items.extend([
                ComplianceItem(
                    item_id="backflow_cert",
                    name="Backflow Certification",
                    compliance_type=ComplianceType.CERTIFICATION,
                    description="Annual backflow tester certification",
                    due_date=datetime(2025, 9, 30),
                    last_completed=datetime(2024, 9, 30),
                    status=RiskLevel.COMPLIANT,
                    action_required="None until September",
                    estimated_cost=75,
                    trade_specific="Plumbing"
                )
            ])
            
        # Add state-specific items
        if client.state == "GA":
            items.append(
                ComplianceItem(
                    item_id="ga_contractor_license",
                    name="Georgia Contractor License",
                    compliance_type=ComplianceType.LICENSE,
                    description="State contractor license renewal",
                    due_date=datetime(2025, 6, 30),
                    last_completed=datetime(2023, 6, 30),
                    status=RiskLevel.MEDIUM,
                    action_required="Complete 8 hours CE before renewal",
                    estimated_cost=175,
                    state_specific="GA",
                    notes="4 of 8 CE hours completed"
                )
            )
            
        return items
        
    def _calculate_overall_status(self, items: List[ComplianceItem]) -> str:
        """Calculate overall compliance status."""
        critical = any(i.status == RiskLevel.CRITICAL for i in items)
        high = any(i.status == RiskLevel.HIGH for i in items)
        
        if critical:
            return "CRITICAL - Immediate attention required"
        elif high:
            return "ATTENTION - Action needed soon"
        else:
            return "GOOD - All compliance items current"
            
    def _generate_action_items(
        self, 
        items: List[ComplianceItem]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized action items."""
        actions = []
        
        for item in sorted(items, key=lambda x: x.status.value):
            actions.append({
                "item": item.name,
                "action": item.action_required,
                "priority": item.status.value,
                "due_date": item.due_date.strftime("%B %d, %Y") if item.due_date else "Ongoing",
                "estimated_cost": item.estimated_cost
            })
            
        return actions
        
    def _item_to_dict(self, item: ComplianceItem) -> Dict[str, Any]:
        """Convert compliance item to dictionary."""
        return {
            "item_id": item.item_id,
            "name": item.name,
            "type": item.compliance_type.value,
            "description": item.description,
            "due_date": item.due_date.isoformat() if item.due_date else None,
            "status": item.status.value,
            "action_required": item.action_required,
            "estimated_cost": item.estimated_cost
        }
        
    def _load_compliance_requirements(self) -> Dict[str, Any]:
        """Load compliance requirement database."""
        # In production: Load from database
        return {}


# Testing
if __name__ == "__main__":
    async def test_compliance():
        agent = ComplianceAgent()
        
        client = ClientProfile(
            client_id="hvac_001",
            business_name="Cool Comfort HVAC",
            trade="HVAC",
            state="GA",
            chart_of_accounts={},
            tax_classification="S-Corp",
            payroll_frequency="bi-weekly"
        )
        
        # Test compliance status check
        task = Task(
            task_id="test_compliance",
            task_type=AgentType.COMPLIANCE,
            client_id="hvac_001",
            payload={"action": "check_status"}
        )
        
        result = await agent.process(task, client)
        print("=== COMPLIANCE STATUS ===")
        print(json.dumps(result, indent=2, default=str))
        
        # Test workers comp audit prep
        task2 = Task(
            task_id="test_wc_audit",
            task_type=AgentType.COMPLIANCE,
            client_id="hvac_001",
            payload={"action": "workers_comp_audit"}
        )
        
        result2 = await agent.process(task2, client)
        print("\n=== WORKERS COMP AUDIT PREP ===")
        print(json.dumps(result2, indent=2, default=str))
        
    asyncio.run(test_compliance()) len(items),
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low),
                "compliant": len(compliant),
                "overall_status": "critical" if critical else "attention" if high else "good"
            },
            
            "critical_items": [self._item_to_dict(i) for i in critical],
            "high_priority_items": [self._item_to_dict(i) for i in high],
            "upcoming_items": [self._item_to_dict(i) for i in medium + low],
            "compliant_items": [self._item_to_dict(i) for i in compliant],
            
            "immediate_actions": [
                {
                    "item": i.name,
                    "action": i.action_required,
                    "deadline": i.due_date.strftime("%B %d, %Y") if i.due_date else "Immediate",
                    "estimated_cost": i.estimated_cost
                }
                for i in critical + high
            ]
        }
        
    async def _generate_compliance_calendar(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """Generate 12-month compliance calendar."""
        
        items = self._get_applicable_requirements(client)
        
        # Organize by month
        calendar = {}
        for i in range(12):
            month_date = datetime.now() + timedelta(days=30*i)
            month_key = month_date.strftime("%Y-%m")
            calendar[month_key] = []
            
        for item in items:
            if item.due_date:
                month_key = item.due_date.strftime("%Y-%m")
                if month_key in calendar:
                    calendar[month_key].append({
                        "name": item.name,
                        "type": item.compliance_type.value,
                        "due": item.due_date.strftime("%B %d"),
                        "action": item.action_required,
                        "cost": item.estimated_cost
                    })
                    
        return {
            "report_type": "compliance_calendar",
            "client": client.business_name,
            "trade": client.trade,
            "state": client.state,
            "generated_at": datetime.now().isoformat(),
            "calendar": calendar,
            "annual_compliance_cost_estimate": sum(
                i.estimated_cost or 0 for i in items
            )
        }
        
    async def _prepare_workers_comp_audit(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        Prepare materials for workers compensation audit.
        This is a huge pain point for contractors - we make it easy.
        """
        
        # In production: Pull actual payroll data
        return {
            "report_type": "workers_comp_audit_prep",
            "client": client.business_name,
            "audit_year": datetime.now().year,
            "prepared_at": datetime.now().isoformat(),
            
            "payroll_summary": {
                "total_gross_payroll": 185000.00,
                "by_class_code": {
                    "5183": {  # HVAC - Plumbing
                        "description": "Plumbing, Heating, Air Conditioning",
                        "payroll": 145000.00,
                        "estimated_rate": 4.25,
                        "estimated_premium": 6162.50
                    },
                    "8810": {  # Clerical
                        "description": "Clerical Office Employees",
                        "payroll": 40000.00,
                        "estimated_rate": 0.35,
                        "estimated_premium": 140.00
                    }
                },
                "total_estimated_premium": 6302.50
            },
            
            "subcontractor_verification": {
                "status": "complete",
                "subs_with_coi": 3,
                "subs_missing_coi": 1,
                "action_required": "Obtain COI from ABC Electrical before audit"
            },
            
            "documents_prepared": [
                "Quarterly payroll reports",
                "W-2 summary",
                "1099 summary for subcontractors",
                "Certificates of insurance from subs",
                "Class code verification"
            ],
            
            "potential_issues": [
                {
                    "issue": "Subcontractor ABC Electrical missing COI",
                    "risk": "Their payroll may be added to your premium",
                    "estimated_impact": 2500.00,
                    "action": "Request current COI immediately"
                }
            ],
            
            "audit_tips": [
                "Ensure all subcontractor COIs are current and on file",
                "Verify class code assignments are accurate",
                "Have payroll records organized by quarter",
                "Separate owner payroll from employee payroll (S-Corp)"
            ]
        }
        
    async def _manage_insurance_certificates(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """Track and manage insurance certificates."""
        
        certificates = [
            {
                "type": "General Liability",
                "carrier": "State Farm",
                "policy_number": "GL-123456",
                "coverage": "$1,000,000 / $2,000,000",
                "effective": "2024-01-01",
                "expiration": "2025-01-01",
                "days_until_expiration": 180,
                "status": "current",
                "annual_premium": 3200.00
            },
            {
                "type": "Workers Compensation",
                "carrier": "Liberty Mutual",
                "policy_number": "WC-789012",
                "coverage": "Statutory",
                "effective": "2024-03-01",
                "expiration": "2025-03-01",
                "days_until_expiration": 240,
                "status": "current",
                "annual_premium": 6500.00
            },
            {
                "type": "Commercial Auto",
                "carrier": "Progressive",
                "policy_number": "CA-345678",
                "coverage": "$1,000,000 CSL",
                "effective": "2024-06-01",
                "expiration": "2024-12-01",
                "days_until_expiration": 30,
                "status": "renewing_soon",
                "annual_premium": 4800.00
            },
            {
                "type": "Umbrella/Excess",
                "carrier": "State Farm",
                "policy_number": "UMB-901234",
                "coverage": "$2,000,000",
                "effective": "2024-01-01",
                "expiration": "2025-01-01",
                "days_until_expiration": 180,
                "status": "current",
                "annual_premium": 1800.00
            }
        ]
        
        return {
            "report_type": "insurance_certificates",
            "client": client.business_name,
            "generated_at": datetime.now().isoformat(),
            
            "summary": {
                "total_policies": len(certificates),
                "current": len([c for c in certificates if c["status"] == "current"]),
                "renewing_soon": len([c for c in certificates if c["status"] == "renewing_soon"]),
                "expired": len([c for c in certificates if c["status"] == "expired"]),
                "total_annual_premium": sum(c["annual_premium"] for c in certificates)
            },
            
            "policies": certificates,
            
            "alerts": [
                {
                    "policy": "Commercial Auto",
                    "message": "Renewal due in 30 days",
                    "action": "Contact Progressive for renewal quote",
                    "deadline": "2024-11-15"
                }
            ],
            
            "coi_requests": {
                "pending": 2,
                "details": [
                    {"requestor": "ABC Property Management", "requested": "2024-10-15"},
                    {"requestor": "City of LaGrange", "requested": "2024-10-20"}
                ]
            }
        }
        
    async def _get_tax_deadlines(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """Get all upcoming tax deadlines."""
        
        # Tax deadlines vary by entity type
        deadlines = {
            "S-Corp": [
                {"deadline": "March 15", "filing": "Form 1120-S", "description": "S-Corp tax return"},
                {"deadline": "January 31", "filing": "W-2s", "description": "Employee W-2s due"},
                {"deadline": "January 31", "filing": "1099s", "description": "Contractor 1099s due"},
                {"deadline": "Quarterly", "filing": "Form 941", "description": "Payroll tax return"},
                {"deadline": "Quarterly", "filing": "Estimated Tax", "description": "Owner estimated payments"},
            ],
            "LLC": [
                {"deadline": "April 15", "filing": "Schedule C", "description": "Personal return with business"},
                {"deadline": "January 31", "filing": "1099s", "description": "Contractor 1099s due"},
                {"deadline": "Quarterly", "filing": "Estimated Tax", "description": "Estimated tax payments"},
            ],
            "Sole Prop": [
                {"deadline": "April 15", "filing": "Schedule C", "description": "Personal return with business"},
                {"deadline": "January 31", "filing": "1099s", "description": "Contractor 1099s due"},
                {"deadline": "Quarterly", "filing": "Estimated Tax", "description": "Estimated tax payments"},
            ]
        }
        
        entity_deadlines = deadlines.get(client.tax_classification, deadlines["LLC"])
        
        # Calculate next occurrence of each deadline
        upcoming = []
        now = datetime.now()
        
        quarterly_dates = [
            datetime(now.year, 4, 15),
            datetime(now.year, 6, 15),
            datetime(now.year, 9, 15),
            datetime(now.year + 1, 1, 15)
        ]
        
        return {
            "report_type": "tax_deadlines",
            "client": client.business_name,
            "entity_type": client.tax_classification,
            "generated_at": datetime.now().isoformat(),
            
            "annual_deadlines": entity_deadlines,
            
            "upcoming_quarterly": {
                "next_estimated_payment": {
                    "due": quarterly_dates[2].strftime("%B %d, %Y"),
                    "days_until": (quarterly_dates[2] - now).days,
                    "estimated_amount": 4500.00
                },
                "next_941": {
                    "due": "October 31, 2024",
                    "for_quarter": "Q3 2024"
                }
            },
            
            "state_deadlines": {
                "state": client.state,
                "sales_tax": "Monthly - 20th of following month" if client.state == "GA" else "Varies",
                "state_withholding": "Monthly with federal 941"
            },
            
            "year_end_deadlines": [
                {"deadline": "January 31", "task": "Issue W-2s to employees"},
                {"deadline": "January 31", "task": "Issue 1099s to contractors"},
                {"deadline": "February 28", "task": "File W-2s with SSA"},
                {"deadline": "February 28", "task": "File 1099s with IRS"},
                {"deadline": "March 15", "task": "S-Corp return due (or extension)"}
            ]
        }
        
    async def _check_license_status(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """Check status of contractor licenses."""
        
        # Trade-specific license requirements
        trade_licenses = {
            "HVAC": [
                {
                    "license": "HVAC Contractor License",
                    "issuing_body": f"{client.state} Secretary of State",
                    "number": "HVAC-12345",
                    "expiration": "2025-06-30",
                    "renewal_cost": 250.00,
                    "ce_required": True,
                    "ce_hours": 8
                },
                {
                    "license": "EPA 608 Certification",
                    "issuing_body": "EPA",
                    "number": "EPA-67890",
                    "expiration": None,  # Does not expire
                    "renewal_cost": 0,
                    "ce_required": False,
                    "ce_hours": 0
                },
                {
                    "license": "Refrigerant Purchaser Certification",
                    "issuing_body": "EPA",
                    "number": "REF-11111",
                    "expiration": None,
                    "renewal_cost": 0,
                    "ce_required": False,
                    "ce_hours": 0
                }
            ],
            "Plumbing": [
                {
                    "license": "Master Plumber License",
                    "issuing_body": f"{client.state} Board of Plumbing",
                    "number": "MP-12345",
                    "expiration": "2025-03-31",
                    "renewal_cost": 175.00,
                    "ce_required": True,
                    "ce_hours": 6
                },
                {
                    "license": "Backflow Certification",
                    "issuing_body": "State Environmental Agency",
                    "number": "BF-67890",
                    "expiration": "2024-12-31",
                    "renewal_cost": 100.00,
                    "ce_required": True,
                    "ce_hours": 4
                }
            ],
            "Electrical": [
                {
                    "license": "Master Electrician License",
                    "issuing_body": f"{client.state} Board of Electrical Contractors",
                    "number": "ME-12345",
                    "expiration": "2025-09-30",
                    "renewal_cost": 200.00,
                    "ce_required": True,
                    "ce_hours": 12
                }
            ],
            "Roofing": [
                {
                    "license": "Roofing Contractor License",
                    "issuing_body": f"{client.state} Secretary of State",
                    "number": "RC-12345",
                    "expiration": "2025-12-31",
                    "renewal_cost": 300.00,
                    "ce_required": False,
                    "ce_hours": 0
                }
            ]
        }
        
        licenses = trade_licenses.get(client.trade, [])
        
        # Calculate status for each license
        for lic in licenses:
            if lic["expiration"]:
                exp_date = datetime.strptime(lic["expiration"], "%Y-%m-%d")
                days_until = (exp_date - datetime.now()).days
                
                if days_until < 0:
                    lic["status"] = "expired"
                elif days_until < 30:
                    lic["status"] = "critical"
                elif days_until < 90:
                    lic["status"] = "renewing_soon"
                else:
                    lic["status"] = "current"
                    
                lic["days_until_expiration"] = days_until
            else:
                lic["status"] = "permanent"
                lic["days_until_expiration"] = None
                
        return {
            "report_type": "license_status",
            "client": client.business_name,
            "trade": client.trade,
            "state": client.state,
            "generated_at": datetime.now().isoformat(),
            
            "licenses": licenses,
            
            "ce_requirements": {
                "total_hours_due": sum(l["ce_hours"] for l in licenses if l["ce_required"]),
                "next_deadline": "2025-06-30",
                "approved_providers": [
                    "ACCA (Air Conditioning Contractors of America)",
                    f"{client.state} HVAC Association",
                    "Online CE providers (verify state approval)"
                ]
            },
            
            "alerts": [
                {
                    "license": l["license"],
                    "message": f"Expires in {l['days_until_expiration']} days",
                    "action": f"Renew with {l['issuing_body']}",
                    "cost": l["renewal_cost"]
                }
                for l in licenses 
                if l.get("days_until_expiration") and l["days_until_expiration"] < 90
            ]
        }
        
    def _get_applicable_requirements(
        self, 
        client: ClientProfile
    ) -> List[ComplianceItem]:
        """Get all compliance requirements applicable to this client."""
        
        # Base requirements for all contractors
        items = [
            ComplianceItem(
                item_id="business_license",
                name="Business License Renewal",
                compliance_type=ComplianceType.LICENSE,
                description="Annual business license renewal",
                due_date=datetime(2025, 1, 31),
                last_completed=datetime(2024, 1, 15),
                status=RiskLevel.LOW,
                action_required="Renew business license with city",
                estimated_cost=150.00
            ),
            ComplianceItem(
                item_id="general_liability",
                name="General Liability Insurance",
                compliance_type=ComplianceType.INSURANCE,
                description="GL insurance policy renewal",
                due_date=datetime(2025, 1, 1),
                last_completed=datetime(2024, 1, 1),
                status=RiskLevel.MEDIUM,
                action_required="Review and renew GL policy",
                estimated_cost=3200.00
            ),
            ComplianceItem(
                item_id="workers_comp",
                name="Workers Comp Insurance",
                compliance_type=ComplianceType.INSURANCE,
                description="Workers compensation policy",
                due_date=datetime(2025, 3, 1),
                last_completed=datetime(2024, 3, 1),
                status=RiskLevel.LOW,
                action_required="Renew workers comp policy",
                estimated_cost=6500.00
            ),
            ComplianceItem(
                item_id="wc_audit",
                name="Workers Comp Annual Audit",
                compliance_type=ComplianceType.AUDIT,
                description="Annual premium audit",
                due_date=datetime(2025, 4, 1),
                last_completed=datetime(2024, 4, 15),
                status=RiskLevel.LOW,
                action_required="Prepare payroll records for audit",
                estimated_cost=0
            ),
        ]
        
        # Trade-specific requirements
        if client.trade == "HVAC":
            items.extend([
                ComplianceItem(
                    item_id="epa_608",
                    name="EPA 608 Certification",
                    compliance_type=ComplianceType.CERTIFICATION,
                    description="Refrigerant handling certification",
                    due_date=None,  # Does not expire
                    last_completed=datetime(2020, 5, 1),
                    status=RiskLevel.COMPLIANT,
                    action_required="None - certification is permanent",
                    estimated_cost=0,
                    trade_specific="HVAC"
                ),
                ComplianceItem(
                    item_id="hvac_license",
                    name="HVAC Contractor License",
                    compliance_type=ComplianceType.LICENSE,
                    description="State HVAC contractor license",
                    due_date=datetime(2025, 6, 30),
                    last_completed=datetime(2023, 6, 15),
                    status=RiskLevel.LOW,
                    action_required="Complete CE hours and renew",
                    estimated_cost=250.00,
                    trade_specific="HVAC"
                ),
            ])
            
        # State-specific requirements
        if client.state == "GA":
            items.append(
                ComplianceItem(
                    item_id="ga_sos_renewal",
                    name="Georgia SOS Annual Registration",
                    compliance_type=ComplianceType.REGISTRATION,
                    description="Annual registration with Secretary of State",
                    due_date=datetime(2025, 4, 1),
                    last_completed=datetime(2024, 3, 15),
                    status=RiskLevel.LOW,
                    action_required="File annual registration online",
                    estimated_cost=50.00,
                    state_specific="GA"
                )
            )
            
        # Recalculate status based on current date
        for item in items:
            if item.due_date:
                days_until = (item.due_date - datetime.now()).days
                if days_until < 0:
                    item.status = RiskLevel.CRITICAL
                elif days_until < 7:
                    item.status = RiskLevel.CRITICAL
                elif days_until < 30:
                    item.status = RiskLevel.HIGH
                elif days_until < 60:
                    item.status = RiskLevel.MEDIUM
                else:
                    item.status = RiskLevel.LOW
                    
        return items
        
    def _load_compliance_requirements(self) -> Dict[str, Any]:
        """Load compliance requirement database."""
        return {}
        
    def _item_to_dict(self, item: ComplianceItem) -> Dict[str, Any]:
        """Convert compliance item to dictionary."""
        return {
            "item_id": item.item_id,
            "name": item.name,
            "type": item.compliance_type.value,
            "description": item.description,
            "due_date": item.due_date.isoformat() if item.due_date else None,
            "status": item.status.value,
            "action_required": item.action_required,
            "estimated_cost": item.estimated_cost
        }


# Testing
if __name__ == "__main__":
    async def test_compliance():
        agent = ComplianceAgent()
        
        client = ClientProfile(
            client_id="hvac_001",
            business_name="Cool Comfort HVAC",
            trade="HVAC",
            state="GA",
            chart_of_accounts={},
            tax_classification="S-Corp",
            payroll_frequency="bi-weekly"
        )
        
        # Test compliance status
        task = Task(
            task_id="test_compliance",
            task_type=AgentType.COMPLIANCE,
            client_id="hvac_001",
            payload={"action": "check_status"}
        )
        
        result = await agent.process(task, client)
        print("=== COMPLIANCE STATUS ===")
        print(json.dumps(result, indent=2, default=str))
        
        # Test workers comp audit prep
        task2 = Task(
            task_id="test_wc",
            task_type=AgentType.COMPLIANCE,
            client_id="hvac_001",
            payload={"action": "workers_comp_audit"}
        )
        
        result2 = await agent.process(task2, client)
        print("\n=== WORKERS COMP AUDIT PREP ===")
        print(json.dumps(result2, indent=2, default=str))
        
    asyncio.run(test_compliance())
