"""
Fynix Systems - Categorization Agent
====================================
Intelligent transaction categorization with deep contractor trade knowledge.

Blue Ocean Differentiator: Generic bookkeeping software uses basic rules.
This agent understands HVAC vs Plumbing vs Roofing expense patterns and
categorizes with trade-specific precision that generalists can't match.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import json
import re
import logging

from agents.orchestrator import BaseAgent, Task, ClientProfile, AgentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CategorizationAgent")


@dataclass
class CategoryRule:
    """A categorization rule with confidence weighting."""
    pattern: str
    category: str
    subcategory: Optional[str] = None
    confidence: float = 0.9
    trade_specific: Optional[str] = None  # None = applies to all trades
    tax_relevant: bool = False
    notes: Optional[str] = None


@dataclass
class CategorizedTransaction:
    """Transaction with category assignment."""
    transaction_id: str
    original_data: Dict[str, Any]
    category: str
    subcategory: Optional[str]
    confidence: float
    auto_approved: bool
    reasoning: str
    tax_flags: List[str] = field(default_factory=list)
    job_id: Optional[str] = None
    alternative_categories: List[Tuple[str, float]] = field(default_factory=list)


class CategorizationAgent(BaseAgent):
    """
    Categorization Agent - Smart transaction classification.
    
    Key capabilities:
    - Trade-specific expense recognition
    - Vendor-based categorization
    - Amount-based heuristics
    - Job costing allocation
    - Tax-relevant flagging
    - Learning from corrections
    """
    
    # Confidence threshold for auto-approval
    AUTO_APPROVE_THRESHOLD = 0.90
    
    def __init__(self):
        super().__init__(AgentType.CATEGORIZATION)
        self.rules = self._load_categorization_rules()
        self.vendor_category_map = self._load_vendor_mappings()
        self.client_overrides = {}  # Client-specific learned patterns
        
    async def process(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """Categorize incoming transactions."""
        source_result = task.payload.get("source_result", {})
        transactions = source_result.get("transactions", [])
        
        if not transactions:
            return {"status": "no_transactions", "categorized": []}
            
        categorized = []
        for txn in transactions:
            result = await self._categorize_transaction(txn, client)
            categorized.append(result)
            
        # Summary stats
        auto_approved = len([c for c in categorized if c.auto_approved])
        needs_review = len(categorized) - auto_approved
        
        return {
            "status": "success",
            "total_processed": len(categorized),
            "auto_approved": auto_approved,
            "needs_review": needs_review,
            "categorized": [self._to_dict(c) for c in categorized]
        }
        
    async def _categorize_transaction(
        self, 
        txn: Dict[str, Any], 
        client: ClientProfile
    ) -> CategorizedTransaction:
        """
        Multi-factor categorization logic.
        
        Priority order:
        1. Client-specific learned patterns
        2. Vendor-based mapping
        3. Trade-specific rules
        4. Generic pattern matching
        5. Amount-based heuristics
        """
        vendor = txn.get("vendor_payee", "")
        description = txn.get("description", "")
        amount = txn.get("amount", 0)
        
        # Track all potential matches
        candidates = []
        
        # 1. Check client-specific overrides first
        client_key = f"{client.client_id}:{vendor}"
        if client_key in self.client_overrides:
            override = self.client_overrides[client_key]
            candidates.append((
                override["category"],
                override.get("subcategory"),
                0.98,
                "Client-specific learned pattern"
            ))
            
        # 2. Vendor-based mapping
        if vendor:
            vendor_match = self._match_vendor(vendor, client.trade)
            if vendor_match:
                candidates.append(vendor_match)
                
        # 3. Trade-specific pattern matching
        trade_match = self._match_trade_patterns(
            description, 
            amount, 
            client.trade
        )
        if trade_match:
            candidates.append(trade_match)
            
        # 4. Generic pattern matching
        generic_match = self._match_generic_patterns(description, amount)
        if generic_match:
            candidates.append(generic_match)
            
        # 5. Amount-based heuristics
        amount_hint = self._amount_heuristics(amount, client.trade)
        if amount_hint:
            candidates.append(amount_hint)
            
        # Select best match
        if candidates:
            # Sort by confidence
            candidates.sort(key=lambda x: x[2], reverse=True)
            best = candidates[0]
            
            return CategorizedTransaction(
                transaction_id=txn.get("external_id", "unknown"),
                original_data=txn,
                category=best[0],
                subcategory=best[1],
                confidence=best[2],
                auto_approved=best[2] >= self.AUTO_APPROVE_THRESHOLD,
                reasoning=best[3],
                tax_flags=self._check_tax_flags(best[0], amount, client),
                alternative_categories=[
                    (c[0], c[2]) for c in candidates[1:4]  # Top 3 alternatives
                ]
            )
        else:
            # Uncategorized - needs human review
            return CategorizedTransaction(
                transaction_id=txn.get("external_id", "unknown"),
                original_data=txn,
                category="UNCATEGORIZED",
                subcategory=None,
                confidence=0.0,
                auto_approved=False,
                reasoning="No matching patterns found",
                tax_flags=[],
                alternative_categories=[]
            )
            
    def _match_vendor(
        self, 
        vendor: str, 
        trade: str
    ) -> Optional[Tuple[str, Optional[str], float, str]]:
        """Match vendor to category."""
        vendor_upper = vendor.upper()
        
        # Check vendor mapping
        for pattern, mapping in self.vendor_category_map.items():
            if re.search(pattern, vendor_upper):
                # Check if trade-specific override exists
                if trade in mapping.get("trade_overrides", {}):
                    override = mapping["trade_overrides"][trade]
                    return (
                        override["category"],
                        override.get("subcategory"),
                        0.95,
                        f"Vendor match with {trade} override"
                    )
                return (
                    mapping["category"],
                    mapping.get("subcategory"),
                    0.92,
                    f"Vendor pattern match: {pattern}"
                )
        return None
        
    def _match_trade_patterns(
        self, 
        description: str, 
        amount: float, 
        trade: str
    ) -> Optional[Tuple[str, Optional[str], float, str]]:
        """Match based on trade-specific patterns."""
        
        trade_patterns = {
            "HVAC": {
                r"REFRIGERANT|R-?22|R-?410A|PURON|FREON": (
                    "Cost of Goods Sold", "Refrigerant", 0.95
                ),
                r"COMPRESSOR|CONDENSER|EVAPORATOR": (
                    "Cost of Goods Sold", "Equipment Parts", 0.93
                ),
                r"THERMOSTAT|NEST|ECOBEE|HONEYWELL": (
                    "Cost of Goods Sold", "Controls & Thermostats", 0.92
                ),
                r"DUCTWORK|FLEX\s*DUCT|SHEET\s*METAL": (
                    "Cost of Goods Sold", "Ductwork Materials", 0.91
                ),
                r"CARRIER|LENNOX|TRANE|RHEEM|GOODMAN": (
                    "Cost of Goods Sold", "Equipment Purchase", 0.94
                ),
            },
            "Plumbing": {
                r"PVC|CPVC|PEX|COPPER\s*PIPE": (
                    "Cost of Goods Sold", "Pipe & Fittings", 0.94
                ),
                r"WATER\s*HEATER|TANKLESS": (
                    "Cost of Goods Sold", "Water Heaters", 0.95
                ),
                r"FAUCET|FIXTURE|TOILET|SINK": (
                    "Cost of Goods Sold", "Fixtures", 0.93
                ),
                r"SEWER|DRAIN|ROOTER": (
                    "Cost of Goods Sold", "Drain Services", 0.91
                ),
            },
            "Roofing": {
                r"SHINGLE|ARCHITECTURAL|3-?TAB": (
                    "Cost of Goods Sold", "Roofing Materials - Shingles", 0.95
                ),
                r"UNDERLAYMENT|FELT|ICE\s*(AND|&)\s*WATER": (
                    "Cost of Goods Sold", "Roofing Materials - Underlayment", 0.93
                ),
                r"FLASHING|DRIP\s*EDGE|VALLEY": (
                    "Cost of Goods Sold", "Roofing Materials - Metal", 0.92
                ),
                r"DUMPSTER|DISPOSAL|DUMP": (
                    "Job Costs", "Disposal & Cleanup", 0.91
                ),
            },
            "Electrical": {
                r"WIRE|ROMEX|CONDUIT|MC\s*CABLE": (
                    "Cost of Goods Sold", "Wire & Cable", 0.94
                ),
                r"BREAKER|PANEL|LOAD\s*CENTER": (
                    "Cost of Goods Sold", "Electrical Panels", 0.95
                ),
                r"OUTLET|SWITCH|RECEPTACLE|GFCI": (
                    "Cost of Goods Sold", "Devices", 0.92
                ),
                r"FIXTURE|LIGHT|LED|CEILING\s*FAN": (
                    "Cost of Goods Sold", "Lighting", 0.91
                ),
            }
        }
        
        patterns = trade_patterns.get(trade, {})
        description_upper = description.upper()
        
        for pattern, (category, subcategory, confidence) in patterns.items():
            if re.search(pattern, description_upper):
                return (category, subcategory, confidence, f"Trade-specific pattern: {trade}")
                
        return None
        
    def _match_generic_patterns(
        self, 
        description: str, 
        amount: float
    ) -> Optional[Tuple[str, Optional[str], float, str]]:
        """Match generic expense patterns applicable to all trades."""
        
        patterns = {
            # Vehicle & Fuel
            r"SHELL|EXXON|CHEVRON|BP\s|RACETRAC|QUIKTRIP|QT\s|WAWA|PILOT|LOVES": (
                "Vehicle Expenses", "Fuel", 0.94
            ),
            r"OIL\s*CHANGE|JIFFY|VALVOLINE|TIRE|FIRESTONE|GOODYEAR|DISCOUNT\s*TIRE": (
                "Vehicle Expenses", "Maintenance", 0.92
            ),
            r"AUTOZONE|O\'?REILLY|ADVANCE\s*AUTO|NAPA": (
                "Vehicle Expenses", "Parts & Supplies", 0.91
            ),
            
            # Office & Admin
            r"OFFICE\s*DEPOT|STAPLES|OFFICE\s*MAX": (
                "Office Expenses", "Office Supplies", 0.93
            ),
            r"QUICKBOOKS|XERO|FRESHBOOKS|WAVE": (
                "Office Expenses", "Accounting Software", 0.95
            ),
            r"MICROSOFT|GOOGLE\s*WORKSPACE|ADOBE|DROPBOX": (
                "Office Expenses", "Software Subscriptions", 0.93
            ),
            
            # Insurance & Professional
            r"STATE\s*FARM|ALLSTATE|PROGRESSIVE|GEICO|LIBERTY\s*MUTUAL": (
                "Insurance", None, 0.90
            ),
            r"WORKERS\s*COMP|WORK\s*COMP|W/?C\s*PREMIUM": (
                "Insurance", "Workers Compensation", 0.95
            ),
            
            # Tools & Equipment
            r"HARBOR\s*FREIGHT|NORTHERN\s*TOOL|GRAINGER": (
                "Tools & Equipment", None, 0.90
            ),
            r"MILWAUKEE|DEWALT|MAKITA|RYOBI|BOSCH": (
                "Tools & Equipment", "Power Tools", 0.92
            ),
            
            # Meals & Entertainment
            r"MCDONALD|BURGER\s*KING|WENDY|CHICK-?FIL|SUBWAY|TACO\s*BELL": (
                "Meals & Entertainment", "Team Meals", 0.85
            ),
            
            # Utilities & Telecom
            r"AT&?T|VERIZON|T-?MOBILE|SPRINT": (
                "Utilities", "Phone/Cellular", 0.93
            ),
            r"COMCAST|SPECTRUM|XFINITY|CHARTER": (
                "Utilities", "Internet", 0.92
            ),
        }
        
        description_upper = description.upper()
        
        for pattern, (category, subcategory, confidence) in patterns.items():
            if re.search(pattern, description_upper):
                return (category, subcategory, confidence, f"Generic pattern match")
                
        return None
        
    def _amount_heuristics(
        self, 
        amount: float, 
        trade: str
    ) -> Optional[Tuple[str, Optional[str], float, str]]:
        """Use amount patterns to suggest category."""
        
        abs_amount = abs(amount)
        
        # Very small amounts are often supplies or fuel
        if abs_amount < 50:
            return (
                "Operating Expenses", 
                "Miscellaneous", 
                0.4,  # Low confidence - just a hint
                "Small amount heuristic"
            )
            
        # Large equipment purchases (trade-specific thresholds)
        equipment_thresholds = {
            "HVAC": 2000,      # AC units
            "Plumbing": 500,   # Water heaters
            "Roofing": 1000,   # Material loads
            "Electrical": 300, # Panels
        }
        
        threshold = equipment_thresholds.get(trade, 1000)
        
        if abs_amount > threshold:
            return (
                "Cost of Goods Sold",
                "Materials - Large Purchase",
                0.5,  # Medium-low confidence
                f"Large purchase heuristic (>${threshold})"
            )
            
        return None
        
    def _check_tax_flags(
        self, 
        category: str, 
        amount: float, 
        client: ClientProfile
    ) -> List[str]:
        """Flag transactions with tax implications."""
        flags = []
        
        # Section 179 equipment
        if abs(amount) > 2500 and category in ["Tools & Equipment", "Cost of Goods Sold"]:
            flags.append("POTENTIAL_SECTION_179")
            
        # De minimis safe harbor
        if abs(amount) <= 2500 and category in ["Tools & Equipment"]:
            flags.append("DE_MINIMIS_SAFE_HARBOR")
            
        # Meals - 50% deductible
        if "Meals" in category:
            flags.append("MEALS_50_PERCENT_DEDUCTIBLE")
            
        # Vehicle expenses - needs mileage tracking
        if "Vehicle" in category:
            flags.append("VEHICLE_EXPENSE_TRACK_MILEAGE")
            
        return flags
        
    def _load_categorization_rules(self) -> List[CategoryRule]:
        """Load categorization rules."""
        # In production: Load from database
        return []
        
    def _load_vendor_mappings(self) -> Dict[str, Dict[str, Any]]:
        """
        Load vendor to category mappings.
        This is the "knowledge base" that makes the system smart.
        """
        return {
            # Supply Houses
            r"HOME\s*DEPOT": {
                "category": "Cost of Goods Sold",
                "subcategory": "Materials & Supplies",
                "trade_overrides": {
                    "HVAC": {"category": "Cost of Goods Sold", "subcategory": "HVAC Supplies"},
                    "Plumbing": {"category": "Cost of Goods Sold", "subcategory": "Plumbing Supplies"},
                }
            },
            r"LOWE\'?S": {
                "category": "Cost of Goods Sold",
                "subcategory": "Materials & Supplies"
            },
            r"GRAINGER": {
                "category": "Cost of Goods Sold",
                "subcategory": "Industrial Supplies"
            },
            r"FERGUSON": {
                "category": "Cost of Goods Sold",
                "subcategory": "Plumbing Supplies",
                "trade_overrides": {
                    "HVAC": {"category": "Cost of Goods Sold", "subcategory": "HVAC Equipment"}
                }
            },
            r"JOHNSTONE": {
                "category": "Cost of Goods Sold",
                "subcategory": "HVAC Supplies"
            },
            r"WINSUPPLY|WIN\s*SUPPLY": {
                "category": "Cost of Goods Sold",
                "subcategory": "Trade Supplies"
            },
            
            # Equipment Rental
            r"UNITED\s*RENTALS": {
                "category": "Equipment Rental",
                "subcategory": None
            },
            r"SUNBELT": {
                "category": "Equipment Rental",
                "subcategory": None
            },
            r"HOME\s*DEPOT\s*RENTAL|TOOL\s*RENTAL": {
                "category": "Equipment Rental",
                "subcategory": None
            },
        }
        
    async def learn_from_correction(
        self, 
        client_id: str, 
        transaction_id: str,
        original_category: str,
        corrected_category: str,
        corrected_subcategory: Optional[str],
        vendor: str
    ):
        """
        Learn from human corrections to improve future categorization.
        This is how the system gets smarter over time.
        """
        client_key = f"{client_id}:{vendor}"
        
        self.client_overrides[client_key] = {
            "category": corrected_category,
            "subcategory": corrected_subcategory,
            "learned_from": transaction_id,
            "learned_at": datetime.now().isoformat()
        }
        
        self.logger.info(
            f"Learned pattern: {vendor} -> {corrected_category}/{corrected_subcategory}"
        )
        
    def _to_dict(self, cat: CategorizedTransaction) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "transaction_id": cat.transaction_id,
            "original_data": cat.original_data,
            "category": cat.category,
            "subcategory": cat.subcategory,
            "confidence": cat.confidence,
            "auto_approved": cat.auto_approved,
            "reasoning": cat.reasoning,
            "tax_flags": cat.tax_flags,
            "job_id": cat.job_id,
            "alternative_categories": cat.alternative_categories
        }


# Testing
if __name__ == "__main__":
    async def test_categorization():
        agent = CategorizationAgent()
        
        client = ClientProfile(
            client_id="hvac_001",
            business_name="Cool Comfort HVAC",
            trade="HVAC",
            state="GA",
            chart_of_accounts={},
            tax_classification="S-Corp",
            payroll_frequency="bi-weekly"
        )
        
        test_transactions = [
            {
                "external_id": "txn_001",
                "vendor_payee": "Johnstone Supply",
                "description": "JOHNSTONE SUPPLY #1234 R-410A REFRIGERANT",
                "amount": -245.67
            },
            {
                "external_id": "txn_002",
                "vendor_payee": "Shell Gas",
                "description": "SHELL OIL 123456789",
                "amount": -65.00
            },
            {
                "external_id": "txn_003",
                "vendor_payee": "The Home Depot",
                "description": "HOME DEPOT #4567",
                "amount": -189.43
            },
            {
                "external_id": "txn_004",
                "vendor_payee": "Unknown Vendor",
                "description": "PAYMENT TO XYZ CORP",
                "amount": -500.00
            },
            {
                "external_id": "txn_005",
                "vendor_payee": "Carrier HVAC",
                "description": "CARRIER ENT - 3 TON UNIT",
                "amount": -4500.00
            }
        ]
        
        task = Task(
            task_id="test_cat",
            task_type=AgentType.CATEGORIZATION,
            client_id="hvac_001",
            payload={
                "source_result": {
                    "transactions": test_transactions
                }
            }
        )
        
        result = await agent.process(task, client)
        print(json.dumps(result, indent=2, default=str))
        
    asyncio.run(test_categorization())
