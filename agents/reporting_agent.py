"""
Fynix Systems - Reporting Agent
===============================
Transforms bookkeeping data into actionable executive intelligence.

Blue Ocean Differentiator: This is the "Post-Export" solution.
While competitors export CSVs and PDFs, we generate:
- Executive dashboards
- Cash flow forecasts
- Job profitability analysis
- Tax planning insights
- Automated board/bank-ready reports
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
import logging

from agents.orchestrator import BaseAgent, Task, ClientProfile, AgentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReportingAgent")


@dataclass
class FinancialMetrics:
    """Core financial metrics for a period."""
    period_start: datetime
    period_end: datetime
    revenue: float
    cogs: float
    gross_profit: float
    gross_margin: float
    operating_expenses: float
    net_income: float
    net_margin: float
    cash_position: float
    accounts_receivable: float
    accounts_payable: float
    

@dataclass
class JobProfitability:
    """Job costing analysis for contractors."""
    job_id: str
    job_name: str
    customer: str
    contract_amount: float
    costs_to_date: float
    revenue_recognized: float
    gross_profit: float
    margin_percentage: float
    estimated_completion: float  # 0-100%
    projected_final_margin: float


@dataclass
class CashFlowProjection:
    """Weekly cash flow projection."""
    week_starting: datetime
    beginning_cash: float
    expected_inflows: float
    expected_outflows: float
    ending_cash: float
    notes: List[str] = field(default_factory=list)


class ReportingAgent(BaseAgent):
    """
    Reporting Agent - Executive intelligence from raw bookkeeping data.
    
    Report Types:
    - Flash Report (Weekly executive summary)
    - Monthly Financial Package
    - Job Profitability Analysis
    - Cash Flow Forecast
    - Tax Planning Summary
    - Bank/Loan Ready Packages
    - Custom KPI Dashboards
    """
    
    def __init__(self):
        super().__init__(AgentType.REPORTING)
        
    async def process(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """Generate requested report."""
        report_type = task.payload.get("report_type", "flash")
        
        report_handlers = {
            "flash": self._generate_flash_report,
            "monthly": self._generate_monthly_package,
            "job_profitability": self._generate_job_profitability,
            "cash_flow": self._generate_cash_flow_forecast,
            "tax_planning": self._generate_tax_planning_report,
            "bank_ready": self._generate_bank_ready_package,
            "kpi_dashboard": self._generate_kpi_dashboard,
        }
        
        handler = report_handlers.get(report_type, self._generate_flash_report)
        return await handler(task, client)
        
    async def _generate_flash_report(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        Weekly Flash Report - The contractor's "vital signs."
        
        What busy contractors need to see in 30 seconds:
        1. Cash position
        2. This week's revenue vs. last week
        3. Outstanding receivables (who owes me?)
        4. Upcoming payables (what do I owe?)
        5. Active jobs status
        """
        
        # In production: Query actual ledger data
        metrics = await self._calculate_current_metrics(client)
        
        report = {
            "report_type": "flash",
            "generated_at": datetime.now().isoformat(),
            "client": client.business_name,
            "period": "Week Ending " + datetime.now().strftime("%B %d, %Y"),
            
            "vital_signs": {
                "cash_position": {
                    "current": metrics.cash_position,
                    "change_from_last_week": 2340.00,  # Example
                    "status": "healthy" if metrics.cash_position > 10000 else "attention"
                },
                "revenue_this_week": {
                    "amount": 12500.00,
                    "vs_last_week": "+15%",
                    "vs_average": "+8%"
                },
                "gross_margin": {
                    "current": f"{metrics.gross_margin:.1%}",
                    "target": "45%",
                    "status": "on_track" if metrics.gross_margin >= 0.40 else "below_target"
                }
            },
            
            "accounts_receivable": {
                "total": metrics.accounts_receivable,
                "aging": {
                    "current": 8500.00,
                    "30_days": 3200.00,
                    "60_days": 1500.00,
                    "90_plus": 800.00
                },
                "action_items": [
                    "Follow up: Johnson Residence - $2,100 (45 days)",
                    "Final notice: ABC Property Mgmt - $800 (92 days)"
                ]
            },
            
            "accounts_payable": {
                "total": metrics.accounts_payable,
                "due_this_week": 4200.00,
                "due_next_week": 3800.00,
                "critical": [
                    "Johnstone Supply - $1,850 due Friday"
                ]
            },
            
            "active_jobs": {
                "count": 5,
                "total_contract_value": 78500.00,
                "highlight": "Smith HVAC Replacement - 75% complete, on schedule"
            },
            
            "alerts": [
                {
                    "type": "cash_flow",
                    "message": "Payroll Friday: Ensure $4,200 available",
                    "severity": "info"
                },
                {
                    "type": "receivable", 
                    "message": "ABC Property Mgmt invoice approaching 90 days",
                    "severity": "warning"
                }
            ]
        }
        
        return report
        
    async def _generate_monthly_package(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        Monthly Financial Package - Complete financial picture.
        
        Includes:
        - Income Statement (P&L)
        - Balance Sheet
        - Cash Flow Statement
        - Budget vs. Actual
        - Trend Analysis
        - Management Commentary
        """
        
        period = task.payload.get("period", datetime.now().strftime("%Y-%m"))
        
        report = {
            "report_type": "monthly_package",
            "client": client.business_name,
            "period": period,
            "generated_at": datetime.now().isoformat(),
            
            "income_statement": {
                "revenue": {
                    "service_revenue": 42500.00,
                    "installation_revenue": 28000.00,
                    "maintenance_contracts": 3500.00,
                    "total_revenue": 74000.00
                },
                "cost_of_goods_sold": {
                    "materials": 18500.00,
                    "labor_direct": 12000.00,
                    "subcontractors": 5200.00,
                    "equipment_rental": 1800.00,
                    "total_cogs": 37500.00
                },
                "gross_profit": 36500.00,
                "gross_margin": 0.493,
                
                "operating_expenses": {
                    "payroll_admin": 8500.00,
                    "vehicle_expenses": 3200.00,
                    "insurance": 2100.00,
                    "office_rent": 1500.00,
                    "utilities": 450.00,
                    "software_subscriptions": 350.00,
                    "professional_fees": 500.00,
                    "marketing": 800.00,
                    "other": 600.00,
                    "total_opex": 18000.00
                },
                
                "net_income": 18500.00,
                "net_margin": 0.250
            },
            
            "balance_sheet": {
                "assets": {
                    "current": {
                        "cash": 34500.00,
                        "accounts_receivable": 28000.00,
                        "inventory": 5500.00,
                        "prepaid_expenses": 2200.00,
                        "total_current": 70200.00
                    },
                    "fixed": {
                        "vehicles": 85000.00,
                        "equipment": 35000.00,
                        "less_depreciation": -42000.00,
                        "total_fixed": 78000.00
                    },
                    "total_assets": 148200.00
                },
                "liabilities": {
                    "current": {
                        "accounts_payable": 12500.00,
                        "accrued_expenses": 4200.00,
                        "current_portion_debt": 8400.00,
                        "total_current": 25100.00
                    },
                    "long_term": {
                        "vehicle_loans": 32000.00,
                        "equipment_loans": 15000.00,
                        "total_long_term": 47000.00
                    },
                    "total_liabilities": 72100.00
                },
                "equity": {
                    "retained_earnings": 57600.00,
                    "current_year_earnings": 18500.00,
                    "total_equity": 76100.00
                }
            },
            
            "budget_vs_actual": {
                "revenue": {"budget": 70000.00, "actual": 74000.00, "variance": 4000.00},
                "gross_margin": {"budget": 0.45, "actual": 0.493, "variance": 0.043},
                "net_income": {"budget": 14000.00, "actual": 18500.00, "variance": 4500.00}
            },
            
            "trends": {
                "revenue_3mo_avg": 71500.00,
                "margin_trend": "improving",
                "cash_trend": "stable"
            },
            
            "management_commentary": [
                "Strong month with revenue exceeding budget by 5.7%",
                "Gross margin improvement driven by better material pricing from Johnstone",
                "A/R aging improved - follow-up process working",
                "Consider hiring additional technician to capture overflow demand"
            ]
        }
        
        return report
        
    async def _generate_job_profitability(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        Job Profitability Analysis - Know which jobs make money.
        
        Critical for contractors who often underprice jobs.
        Shows true profitability including all allocated costs.
        """
        
        # Sample job data
        jobs = [
            JobProfitability(
                job_id="JOB-2024-001",
                job_name="Smith Residence HVAC Replacement",
                customer="John Smith",
                contract_amount=12500.00,
                costs_to_date=5800.00,
                revenue_recognized=9375.00,  # 75% complete
                gross_profit=3575.00,
                margin_percentage=0.381,
                estimated_completion=0.75,
                projected_final_margin=0.36
            ),
            JobProfitability(
                job_id="JOB-2024-002",
                job_name="Office Building Maintenance Contract",
                customer="ABC Property Management",
                contract_amount=24000.00,  # Annual
                costs_to_date=8500.00,
                revenue_recognized=12000.00,  # 6 months
                gross_profit=3500.00,
                margin_percentage=0.292,
                estimated_completion=0.50,
                projected_final_margin=0.30
            ),
            JobProfitability(
                job_id="JOB-2024-003",
                job_name="Restaurant Kitchen Hood Install",
                customer="Downtown Diner",
                contract_amount=8500.00,
                costs_to_date=7200.00,
                revenue_recognized=8500.00,  # Complete
                gross_profit=1300.00,
                margin_percentage=0.153,
                estimated_completion=1.0,
                projected_final_margin=0.153
            ),
        ]
        
        report = {
            "report_type": "job_profitability",
            "client": client.business_name,
            "generated_at": datetime.now().isoformat(),
            
            "summary": {
                "total_active_jobs": len([j for j in jobs if j.estimated_completion < 1.0]),
                "total_contract_value": sum(j.contract_amount for j in jobs),
                "total_costs_to_date": sum(j.costs_to_date for j in jobs),
                "overall_margin": 0.308,
                "jobs_below_target_margin": 2  # Below 35%
            },
            
            "jobs": [
                {
                    "job_id": j.job_id,
                    "job_name": j.job_name,
                    "customer": j.customer,
                    "contract_amount": j.contract_amount,
                    "costs_to_date": j.costs_to_date,
                    "gross_profit": j.gross_profit,
                    "margin": f"{j.margin_percentage:.1%}",
                    "completion": f"{j.estimated_completion:.0%}",
                    "projected_final_margin": f"{j.projected_final_margin:.1%}",
                    "status": "healthy" if j.margin_percentage >= 0.35 else "below_target"
                }
                for j in jobs
            ],
            
            "insights": [
                {
                    "type": "alert",
                    "job": "JOB-2024-003",
                    "message": "Restaurant job completed at 15% margin - significantly below 35% target. Review pricing for similar jobs."
                },
                {
                    "type": "opportunity", 
                    "job": "JOB-2024-002",
                    "message": "Maintenance contract trending at 29% margin. Consider renegotiating at renewal for material cost increases."
                },
                {
                    "type": "success",
                    "job": "JOB-2024-001",
                    "message": "Residential replacement on track at 38% margin. Good benchmark for similar quotes."
                }
            ],
            
            "recommendations": [
                "Review estimating process for commercial kitchen work",
                "Add 5% contingency to all hood installation quotes",
                "Track labor hours more granularly on maintenance contracts"
            ]
        }
        
        return report
        
    async def _generate_cash_flow_forecast(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        12-Week Cash Flow Forecast - Never get surprised by cash crunches.
        
        The #1 killer of contractor businesses is cash flow.
        This shows them exactly when problems are coming.
        """
        
        weeks = []
        current_cash = 34500.00
        
        for i in range(12):
            week_start = datetime.now() + timedelta(weeks=i)
            
            # Simulate varying cash flows
            inflows = 8000 + (i % 3) * 4000  # Varies by week
            
            # Regular outflows
            base_outflows = 6000
            
            # Payroll every 2 weeks
            payroll = 4200 if i % 2 == 0 else 0
            
            # Quarterly insurance (week 4, 8, 12)
            insurance = 2100 if i in [4, 8, 12] else 0
            
            # Estimated taxes (week 6)
            taxes = 3500 if i == 6 else 0
            
            total_outflows = base_outflows + payroll + insurance + taxes
            ending_cash = current_cash + inflows - total_outflows
            
            notes = []
            if payroll > 0:
                notes.append("Payroll")
            if insurance > 0:
                notes.append("Quarterly Insurance")
            if taxes > 0:
                notes.append("Q3 Estimated Taxes")
            if ending_cash < 10000:
                notes.append("LOW CASH WARNING")
                
            weeks.append(CashFlowProjection(
                week_starting=week_start,
                beginning_cash=current_cash,
                expected_inflows=inflows,
                expected_outflows=total_outflows,
                ending_cash=ending_cash,
                notes=notes
            ))
            
            current_cash = ending_cash
            
        report = {
            "report_type": "cash_flow_forecast",
            "client": client.business_name,
            "generated_at": datetime.now().isoformat(),
            "forecast_weeks": 12,
            
            "summary": {
                "current_cash": 34500.00,
                "projected_low": min(w.ending_cash for w in weeks),
                "projected_low_week": min(weeks, key=lambda w: w.ending_cash).week_starting.strftime("%B %d"),
                "minimum_recommended": 15000.00,
                "status": "attention" if min(w.ending_cash for w in weeks) < 15000 else "healthy"
            },
            
            "weekly_projections": [
                {
                    "week": w.week_starting.strftime("%b %d"),
                    "beginning": w.beginning_cash,
                    "inflows": w.expected_inflows,
                    "outflows": w.expected_outflows,
                    "ending": w.ending_cash,
                    "notes": w.notes
                }
                for w in weeks
            ],
            
            "critical_dates": [
                {
                    "date": (datetime.now() + timedelta(weeks=6)).strftime("%B %d"),
                    "event": "Q3 Estimated Tax Payment",
                    "amount": 3500.00,
                    "projected_cash_after": weeks[6].ending_cash
                }
            ],
            
            "recommendations": [
                "Week 6 cash position tight after tax payment - consider accelerating collections",
                "Invoice ABC Property Management now ($2,100 outstanding 45 days)",
                "Consider delaying non-essential equipment purchase until after Week 8"
            ]
        }
        
        return report
        
    async def _generate_tax_planning_report(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        Tax Planning Summary - Proactive tax management.
        
        Most contractors only think about taxes in April.
        This keeps tax planning top of mind year-round.
        """
        
        ytd_income = 145000.00
        ytd_expenses = 98000.00
        ytd_net = ytd_income - ytd_expenses
        
        report = {
            "report_type": "tax_planning",
            "client": client.business_name,
            "tax_classification": client.tax_classification,
            "generated_at": datetime.now().isoformat(),
            "tax_year": datetime.now().year,
            
            "ytd_summary": {
                "gross_revenue": ytd_income,
                "total_expenses": ytd_expenses,
                "net_income": ytd_net,
                "estimated_tax_liability": ytd_net * 0.25,  # Simplified
                "quarterly_payments_made": 12000.00,
                "remaining_estimated_liability": (ytd_net * 0.25) - 12000
            },
            
            "deduction_opportunities": [
                {
                    "category": "Section 179 Equipment",
                    "description": "Equipment purchases eligible for immediate deduction",
                    "ytd_used": 4500.00,
                    "limit": 1160000.00,  # 2024 limit
                    "recommendation": "Consider accelerating equipment purchases before year-end"
                },
                {
                    "category": "Vehicle Expenses",
                    "description": "Standard mileage rate: $0.67/mile (2024)",
                    "ytd_claimed": 8500.00,
                    "recommendation": "Review mileage log - may be under-claiming"
                },
                {
                    "category": "Home Office",
                    "description": "If applicable for S-Corp owner",
                    "current_status": "Not currently claiming",
                    "recommendation": "Review eligibility - could yield $2-3K deduction"
                },
                {
                    "category": "Retirement Contributions",
                    "description": "SEP-IRA or Solo 401(k) contributions",
                    "ytd_contributed": 0,
                    "max_available": min(ytd_net * 0.25, 66000),  # 2024 limits
                    "recommendation": "Strong tax reduction opportunity - consult with CPA"
                }
            ],
            
            "estimated_payments": {
                "q1_paid": 3000.00,
                "q2_paid": 4500.00,
                "q3_paid": 4500.00,
                "q4_due": (ytd_net * 0.25) - 12000,
                "q4_due_date": "January 15, 2025"
            },
            
            "alerts": [
                {
                    "type": "deadline",
                    "message": "Q4 estimated payment due January 15",
                    "amount": (ytd_net * 0.25) - 12000
                },
                {
                    "type": "opportunity",
                    "message": "Retirement contribution deadline: Tax filing deadline",
                    "potential_savings": 5000.00
                }
            ],
            
            "year_end_checklist": [
                "Review equipment purchase timing (Section 179)",
                "Verify mileage logs are complete",
                "Gather receipts for any unreimbursed expenses",
                "Calculate retirement contribution amount",
                "Review health insurance premium deduction (S-Corp)",
                "Schedule year-end meeting with CPA"
            ]
        }
        
        return report
        
    async def _generate_bank_ready_package(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        Bank/Loan Ready Package - Everything needed for financing.
        
        When contractors need a line of credit or equipment loan,
        they scramble to gather documents. This is always ready.
        """
        
        report = {
            "report_type": "bank_ready_package",
            "client": client.business_name,
            "prepared_for": task.payload.get("bank_name", "Lender"),
            "generated_at": datetime.now().isoformat(),
            
            "company_overview": {
                "legal_name": client.business_name,
                "trade": client.trade,
                "state": client.state,
                "tax_id": "XX-XXXXXXX",  # Masked
                "years_in_business": 8,
                "owner": "Owner Name",
                "tax_classification": client.tax_classification
            },
            
            "financial_summary": {
                "annual_revenue_current_year": 280000.00,
                "annual_revenue_prior_year": 245000.00,
                "revenue_growth": "14.3%",
                "gross_margin": "47%",
                "net_margin": "22%",
                "current_ratio": 2.8,
                "debt_to_equity": 0.95
            },
            
            "included_documents": [
                "Profit & Loss Statement - Current Year",
                "Profit & Loss Statement - Prior Year",
                "Balance Sheet - Current",
                "Balance Sheet - Prior Year End",
                "Accounts Receivable Aging",
                "Accounts Payable Aging",
                "Tax Returns - 2 Years (separate attachment)",
                "Bank Statements - 3 Months (separate attachment)"
            ],
            
            "financial_statements": {
                "note": "Full statements included in package"
            },
            
            "loan_readiness_score": {
                "score": 82,
                "out_of": 100,
                "factors": {
                    "revenue_stability": "Strong",
                    "profitability": "Good",
                    "cash_position": "Adequate",
                    "debt_load": "Moderate",
                    "documentation": "Complete"
                }
            }
        }
        
        return report
        
    async def _generate_kpi_dashboard(
        self, 
        task: Task, 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """
        KPI Dashboard - Key performance indicators at a glance.
        Customizable metrics for different contractor types.
        """
        
        trade_kpis = {
            "HVAC": ["Revenue per Service Call", "Average Ticket Size", "Maintenance Agreement Ratio", "Tech Utilization"],
            "Plumbing": ["Revenue per Call", "Callback Rate", "Average Job Value", "Lead Conversion"],
            "Roofing": ["Revenue per Square", "Waste Percentage", "Job Completion Rate", "Crew Productivity"],
            "Electrical": ["Revenue per Man-Hour", "Permit Pass Rate", "Warranty Claims", "Material Markup"]
        }
        
        kpis = trade_kpis.get(client.trade, trade_kpis["HVAC"])
        
        report = {
            "report_type": "kpi_dashboard",
            "client": client.business_name,
            "trade": client.trade,
            "generated_at": datetime.now().isoformat(),
            "period": "Month to Date",
            
            "kpis": {
                "revenue_per_service_call": {
                    "current": 385.00,
                    "target": 400.00,
                    "prior_period": 362.00,
                    "trend": "improving"
                },
                "average_ticket_size": {
                    "current": 1250.00,
                    "target": 1100.00,
                    "prior_period": 1180.00,
                    "trend": "exceeding"
                },
                "gross_margin": {
                    "current": 0.47,
                    "target": 0.45,
                    "prior_period": 0.44,
                    "trend": "exceeding"
                },
                "accounts_receivable_days": {
                    "current": 32,
                    "target": 30,
                    "prior_period": 38,
                    "trend": "improving"
                },
                "tech_utilization": {
                    "current": 0.72,
                    "target": 0.80,
                    "prior_period": 0.68,
                    "trend": "improving"
                },
                "maintenance_agreement_ratio": {
                    "current": 0.35,
                    "target": 0.50,
                    "prior_period": 0.32,
                    "trend": "needs_attention"
                }
            },
            
            "recommended_actions": [
                "Maintenance agreement ratio below target - implement upsell training",
                "Tech utilization improving but still below target - review scheduling efficiency",
                "Strong ticket size - consider case study of top performers"
            ]
        }
        
        return report
        
    async def _calculate_current_metrics(
        self, 
        client: ClientProfile
    ) -> FinancialMetrics:
        """Calculate current financial metrics from ledger data."""
        
        # In production: Query actual ledger
        return FinancialMetrics(
            period_start=datetime.now() - timedelta(days=7),
            period_end=datetime.now(),
            revenue=12500.00,
            cogs=6250.00,
            gross_profit=6250.00,
            gross_margin=0.50,
            operating_expenses=3000.00,
            net_income=3250.00,
            net_margin=0.26,
            cash_position=34500.00,
            accounts_receivable=14000.00,
            accounts_payable=8500.00
        )


# Testing
if __name__ == "__main__":
    async def test_reporting():
        agent = ReportingAgent()
        
        client = ClientProfile(
            client_id="hvac_001",
            business_name="Cool Comfort HVAC",
            trade="HVAC",
            state="GA",
            chart_of_accounts={},
            tax_classification="S-Corp",
            payroll_frequency="bi-weekly"
        )
        
        # Test flash report
        task = Task(
            task_id="test_flash",
            task_type=AgentType.REPORTING,
            client_id="hvac_001",
            payload={"report_type": "flash"}
        )
        
        result = await agent.process(task, client)
        print("=== FLASH REPORT ===")
        print(json.dumps(result, indent=2, default=str))
        
        # Test cash flow forecast
        task2 = Task(
            task_id="test_cashflow",
            task_type=AgentType.REPORTING,
            client_id="hvac_001",
            payload={"report_type": "cash_flow"}
        )
        
        result2 = await agent.process(task2, client)
        print("\n=== CASH FLOW FORECAST ===")
        print(json.dumps(result2, indent=2, default=str))
        
    asyncio.run(test_reporting())
