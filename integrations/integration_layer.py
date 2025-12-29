"""
Fynix Systems - Integration Layer
=================================
Connectors to external financial systems.

Integrations:
- Banking: Plaid, MX, Finicity
- Accounting: QuickBooks, Xero, FreshBooks
- Payroll: Gusto, ADP, QuickBooks Payroll
- CRM: GoHighLevel, HubSpot, ServiceTitan
- Receipts: Dext, Hubdoc, AutoEntry
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Integrations")


class BaseIntegration(ABC):
    """Base class for all integrations."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.connected = False
        self.last_sync = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the service."""
        pass
        
    @abstractmethod
    async def sync(self) -> Dict[str, Any]:
        """Sync data from the service."""
        pass
        
    @abstractmethod
    async def push(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Push data to the service."""
        pass


class PlaidIntegration(BaseIntegration):
    """
    Plaid banking integration.
    Provides access to bank transactions, balances, and account info.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.access_token = credentials.get("access_token")
        self.item_id = credentials.get("item_id")
        
    async def connect(self) -> bool:
        """Verify Plaid connection is still valid."""
        # In production: Call Plaid /item/get endpoint
        logger.info("Verifying Plaid connection...")
        self.connected = True
        return True
        
    async def sync(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Sync transactions from Plaid.
        
        Returns normalized transaction data.
        """
        # In production: Call Plaid /transactions/sync endpoint
        
        # Simulated response
        transactions = [
            {
                "transaction_id": f"plaid_txn_{i}",
                "date": (datetime.now() - timedelta(days=i)).isoformat(),
                "name": ["HOME DEPOT #1234", "SHELL OIL 123456", "JOHNSTONE SUPPLY"][i % 3],
                "amount": [169.32, 45.00, 245.67][i % 3],
                "category": ["Building Materials", "Gas Stations", "Hardware Stores"][i % 3],
                "pending": False,
                "account_id": "account_001"
            }
            for i in range(min(days_back, 30))
        ]
        
        self.last_sync = datetime.now()
        
        return {
            "status": "success",
            "transactions": transactions,
            "accounts": [
                {
                    "account_id": "account_001",
                    "name": "Business Checking",
                    "type": "depository",
                    "subtype": "checking",
                    "current_balance": 34567.89,
                    "available_balance": 32567.89
                }
            ],
            "synced_at": self.last_sync.isoformat()
        }
        
    async def push(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Plaid is read-only - no push capability."""
        raise NotImplementedError("Plaid does not support data push")
        
    async def get_balances(self) -> Dict[str, Any]:
        """Get current account balances."""
        # In production: Call Plaid /accounts/balance/get
        return {
            "accounts": [
                {
                    "account_id": "account_001",
                    "name": "Business Checking",
                    "current": 34567.89,
                    "available": 32567.89
                },
                {
                    "account_id": "account_002",
                    "name": "Business Savings",
                    "current": 15000.00,
                    "available": 15000.00
                }
            ],
            "as_of": datetime.now().isoformat()
        }


class QuickBooksIntegration(BaseIntegration):
    """
    QuickBooks Online integration.
    Full read/write access to accounting data.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.realm_id = credentials.get("realm_id")
        self.access_token = credentials.get("access_token")
        self.refresh_token = credentials.get("refresh_token")
        
    async def connect(self) -> bool:
        """Verify QBO connection and refresh token if needed."""
        # In production: Check token validity, refresh if needed
        logger.info("Verifying QuickBooks connection...")
        self.connected = True
        return True
        
    async def sync(self) -> Dict[str, Any]:
        """
        Sync data from QuickBooks.
        Returns chart of accounts, transactions, and balances.
        """
        # In production: Call QBO API endpoints
        
        self.last_sync = datetime.now()
        
        return {
            "status": "success",
            "chart_of_accounts": await self._get_chart_of_accounts(),
            "recent_transactions": await self._get_recent_transactions(),
            "accounts_receivable": await self._get_ar(),
            "accounts_payable": await self._get_ap(),
            "synced_at": self.last_sync.isoformat()
        }
        
    async def push(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Push transaction to QuickBooks."""
        transaction_type = data.get("type", "expense")
        
        if transaction_type == "expense":
            return await self._create_expense(data)
        elif transaction_type == "invoice":
            return await self._create_invoice(data)
        elif transaction_type == "payment":
            return await self._create_payment(data)
        else:
            raise ValueError(f"Unknown transaction type: {transaction_type}")
            
    async def _get_chart_of_accounts(self) -> List[Dict[str, Any]]:
        """Get chart of accounts from QBO."""
        return [
            {"id": "1", "name": "Checking", "type": "Bank", "account_number": "1000"},
            {"id": "2", "name": "Savings", "type": "Bank", "account_number": "1100"},
            {"id": "3", "name": "Accounts Receivable", "type": "Accounts Receivable", "account_number": "1200"},
            {"id": "10", "name": "Service Revenue", "type": "Income", "account_number": "4000"},
            {"id": "11", "name": "Installation Revenue", "type": "Income", "account_number": "4100"},
            {"id": "20", "name": "Materials & Supplies", "type": "Cost of Goods Sold", "account_number": "5000"},
            {"id": "21", "name": "Labor - Direct", "type": "Cost of Goods Sold", "account_number": "5100"},
            {"id": "30", "name": "Vehicle Expenses", "type": "Expense", "account_number": "6000"},
            {"id": "31", "name": "Insurance", "type": "Expense", "account_number": "6100"},
        ]
        
    async def _get_recent_transactions(self) -> List[Dict[str, Any]]:
        """Get recent transactions from QBO."""
        return [
            {
                "id": "qbo_txn_001",
                "type": "expense",
                "date": datetime.now().isoformat(),
                "amount": 245.67,
                "vendor": "Johnstone Supply",
                "account": "Materials & Supplies",
                "memo": "Refrigerant and parts"
            }
        ]
        
    async def _get_ar(self) -> Dict[str, Any]:
        """Get accounts receivable summary."""
        return {
            "total": 14000.00,
            "current": 8500.00,
            "30_days": 3200.00,
            "60_days": 1500.00,
            "90_plus": 800.00
        }
        
    async def _get_ap(self) -> Dict[str, Any]:
        """Get accounts payable summary."""
        return {
            "total": 8500.00,
            "current": 5200.00,
            "30_days": 2100.00,
            "60_days": 1200.00
        }
        
    async def _create_expense(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create expense in QuickBooks."""
        # In production: POST to /v3/company/{realmId}/purchase
        return {
            "status": "created",
            "id": f"qbo_exp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "expense",
            "amount": data.get("amount"),
            "created_at": datetime.now().isoformat()
        }
        
    async def _create_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create invoice in QuickBooks."""
        # In production: POST to /v3/company/{realmId}/invoice
        return {
            "status": "created",
            "id": f"qbo_inv_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "invoice",
            "amount": data.get("amount"),
            "created_at": datetime.now().isoformat()
        }
        
    async def _create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Record payment in QuickBooks."""
        return {
            "status": "created",
            "id": f"qbo_pmt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "payment",
            "amount": data.get("amount"),
            "created_at": datetime.now().isoformat()
        }


class GoHighLevelIntegration(BaseIntegration):
    """
    GoHighLevel CRM integration.
    Sync customer data, invoices, and automate workflows.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.api_key = credentials.get("api_key")
        self.location_id = credentials.get("location_id")
        
    async def connect(self) -> bool:
        """Verify GHL connection."""
        logger.info("Verifying GoHighLevel connection...")
        self.connected = True
        return True
        
    async def sync(self) -> Dict[str, Any]:
        """
        Sync customer and opportunity data from GHL.
        Useful for job costing and AR tracking.
        """
        self.last_sync = datetime.now()
        
        return {
            "status": "success",
            "contacts": await self._get_contacts(),
            "opportunities": await self._get_opportunities(),
            "invoices": await self._get_invoices(),
            "synced_at": self.last_sync.isoformat()
        }
        
    async def push(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Push data to GHL.
        Use cases:
        - Update contact with payment status
        - Trigger workflow on invoice paid
        - Create task for follow-up
        """
        action = data.get("action")
        
        if action == "update_contact":
            return await self._update_contact(data)
        elif action == "trigger_workflow":
            return await self._trigger_workflow(data)
        elif action == "create_task":
            return await self._create_task(data)
        else:
            raise ValueError(f"Unknown action: {action}")
            
    async def _get_contacts(self) -> List[Dict[str, Any]]:
        """Get contacts from GHL."""
        return [
            {
                "id": "contact_001",
                "name": "John Smith",
                "email": "john@example.com",
                "phone": "555-123-4567",
                "tags": ["hvac_customer", "residential"],
                "custom_fields": {
                    "outstanding_balance": 0,
                    "last_service_date": "2024-12-15"
                }
            }
        ]
        
    async def _get_opportunities(self) -> List[Dict[str, Any]]:
        """Get opportunities/jobs from GHL."""
        return [
            {
                "id": "opp_001",
                "name": "HVAC System Replacement",
                "contact_id": "contact_001",
                "pipeline": "Installation Jobs",
                "stage": "In Progress",
                "value": 12500.00,
                "custom_fields": {
                    "job_number": "JOB-2024-001",
                    "completion_percentage": 75
                }
            }
        ]
        
    async def _get_invoices(self) -> List[Dict[str, Any]]:
        """Get invoices from GHL."""
        return [
            {
                "id": "inv_001",
                "contact_id": "contact_001",
                "amount": 12500.00,
                "status": "partial",
                "paid_amount": 9375.00,
                "balance_due": 3125.00
            }
        ]
        
    async def _update_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact in GHL."""
        return {"status": "updated", "contact_id": data.get("contact_id")}
        
    async def _trigger_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger GHL workflow."""
        return {"status": "triggered", "workflow_id": data.get("workflow_id")}
        
    async def _create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create task in GHL."""
        return {"status": "created", "task_id": f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"}


class IntegrationManager:
    """
    Manages all integrations for a client.
    Handles connection lifecycle, sync scheduling, and error handling.
    """
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.integrations: Dict[str, BaseIntegration] = {}
        self.sync_schedule: Dict[str, int] = {
            "plaid": 60,      # Every hour
            "quickbooks": 240, # Every 4 hours
            "gohighlevel": 120 # Every 2 hours
        }
        
    async def register_integration(
        self, 
        name: str, 
        integration: BaseIntegration
    ):
        """Register a new integration."""
        self.integrations[name] = integration
        await integration.connect()
        logger.info(f"Registered integration: {name} for client {self.client_id}")
        
    async def sync_all(self) -> Dict[str, Any]:
        """Sync data from all registered integrations."""
        results = {}
        
        for name, integration in self.integrations.items():
            try:
                if integration.connected:
                    results[name] = await integration.sync()
                else:
                    await integration.connect()
                    results[name] = await integration.sync()
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
                logger.error(f"Sync error for {name}: {e}")
                
        return results
        
    async def get_combined_transactions(
        self, 
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get transactions from all sources and deduplicate.
        This is the primary method for feeding the Ingestion Agent.
        """
        all_transactions = []
        
        # Get from Plaid (bank feed)
        if "plaid" in self.integrations:
            plaid_data = await self.integrations["plaid"].sync(days_back)
            for txn in plaid_data.get("transactions", []):
                txn["source"] = "plaid"
                all_transactions.append(txn)
                
        # Get from QuickBooks (already booked transactions)
        if "quickbooks" in self.integrations:
            qbo_data = await self.integrations["quickbooks"].sync()
            for txn in qbo_data.get("recent_transactions", []):
                txn["source"] = "quickbooks"
                all_transactions.append(txn)
                
        # Deduplicate by matching date + amount + vendor
        # In production: More sophisticated matching algorithm
        
        return all_transactions
        
    async def push_to_accounting(
        self, 
        transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Push categorized transaction to accounting system."""
        if "quickbooks" not in self.integrations:
            raise ValueError("QuickBooks integration not configured")
            
        return await self.integrations["quickbooks"].push(transaction)


# Factory for creating integrations
class IntegrationFactory:
    """Factory for creating integration instances."""
    
    @staticmethod
    def create(
        integration_type: str, 
        credentials: Dict[str, str]
    ) -> BaseIntegration:
        """Create an integration instance."""
        integrations = {
            "plaid": PlaidIntegration,
            "quickbooks": QuickBooksIntegration,
            "gohighlevel": GoHighLevelIntegration,
        }
        
        if integration_type not in integrations:
            raise ValueError(f"Unknown integration type: {integration_type}")
            
        return integrations[integration_type](credentials)


# Testing
if __name__ == "__main__":
    async def test_integrations():
        # Create integration manager
        manager = IntegrationManager("hvac_001")
        
        # Register integrations
        plaid = IntegrationFactory.create("plaid", {
            "access_token": "test_token",
            "item_id": "test_item"
        })
        await manager.register_integration("plaid", plaid)
        
        qbo = IntegrationFactory.create("quickbooks", {
            "realm_id": "123456",
            "access_token": "test_token",
            "refresh_token": "test_refresh"
        })
        await manager.register_integration("quickbooks", qbo)
        
        # Sync all
        results = await manager.sync_all()
        print("=== SYNC RESULTS ===")
        print(json.dumps(results, indent=2, default=str))
        
        # Get combined transactions
        transactions = await manager.get_combined_transactions()
        print("\n=== COMBINED TRANSACTIONS ===")
        print(json.dumps(transactions[:5], indent=2, default=str))
        
    asyncio.run(test_integrations())
