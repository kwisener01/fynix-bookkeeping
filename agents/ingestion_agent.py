"""
Fynix Systems - Ingestion Agent
===============================
Handles all data intake: bank feeds, receipts, invoices, statements.
This agent is the "eyes" of the system - nothing gets booked without going through here.

Blue Ocean Insight: Traditional bookkeepers spend 40-60% of time on data entry.
This agent eliminates that entirely through intelligent extraction and normalization.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import re
import logging

# Import base classes
from agents.orchestrator import BaseAgent, Task, ClientProfile, AgentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestionAgent")


@dataclass
class RawTransaction:
    """Normalized transaction structure from any source."""
    source: str  # bank_feed, receipt_scan, invoice, manual
    external_id: str
    date: datetime
    amount: float
    description: str
    vendor_payee: Optional[str] = None
    raw_data: Dict[str, Any] = None
    confidence_score: float = 1.0
    requires_review: bool = False


@dataclass 
class IngestionResult:
    """Result of an ingestion operation."""
    source: str
    transactions_processed: int
    transactions_new: int
    transactions_duplicate: int
    transactions_flagged: int
    processing_time_ms: int
    transactions: List[RawTransaction] = None


class IngestionAgent(BaseAgent):
    """
    Ingestion Agent - Autonomous data intake and normalization.
    
    Capabilities:
    - Bank feed API integration (Plaid, MX, Finicity)
    - Receipt/invoice OCR processing
    - Email attachment extraction
    - Statement PDF parsing
    - Duplicate detection
    - Vendor recognition and normalization
    """
    
    def __init__(self):
        super().__init__(AgentType.INGESTION)
        self.vendor_patterns = self._load_vendor_patterns()
        self.known_transactions = {}  # In production: Redis or DB
        
    async def process(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """Main entry point - routes to appropriate ingestion method."""
        action = task.payload.get("action", "sync")
        
        action_map = {
            "initial_sync": self._initial_sync,
            "bank_feed": self._process_bank_feed,
            "receipt_scan": self._process_receipt,
            "invoice_upload": self._process_invoice,
            "statement_pdf": self._process_statement,
            "email_attachment": self._process_email_attachment,
        }
        
        handler = action_map.get(action, self._sync_all)
        result = await handler(task, client)
        
        return result
        
    async def _initial_sync(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """
        Initial client onboarding sync.
        Pulls historical data from all connected sources.
        """
        self.logger.info(f"Starting initial sync for {client.business_name}")
        
        results = {
            "client_id": client.client_id,
            "sync_type": "initial",
            "started_at": datetime.now().isoformat(),
            "sources_synced": [],
            "total_transactions": 0
        }
        
        # Sync from each configured integration
        integrations = client.integration_credentials.keys()
        
        for integration in integrations:
            if integration.startswith("plaid_"):
                bank_result = await self._sync_plaid(client, historical=True)
                results["sources_synced"].append(bank_result)
                results["total_transactions"] += bank_result.get("count", 0)
                
        results["completed_at"] = datetime.now().isoformat()
        return results
        
    async def _process_bank_feed(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """
        Process incoming bank feed data.
        In production: Plaid, MX, or direct bank API integration.
        """
        # Simulated bank feed data structure
        raw_transactions = task.payload.get("transactions", [])
        
        processed = []
        for txn in raw_transactions:
            normalized = await self._normalize_bank_transaction(txn, client)
            
            # Check for duplicates
            if not self._is_duplicate(normalized, client.client_id):
                processed.append(normalized)
                self._mark_seen(normalized, client.client_id)
                
        result = IngestionResult(
            source="bank_feed",
            transactions_processed=len(raw_transactions),
            transactions_new=len(processed),
            transactions_duplicate=len(raw_transactions) - len(processed),
            transactions_flagged=len([t for t in processed if t.requires_review]),
            processing_time_ms=150,
            transactions=processed
        )
        
        return self._result_to_dict(result)
        
    async def _process_receipt(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """
        Process receipt image through OCR and extraction.
        
        Key fields to extract:
        - Vendor name
        - Date
        - Total amount
        - Tax amount (for proper categorization)
        - Line items (when possible)
        - Payment method
        """
        receipt_data = task.payload.get("receipt", {})
        image_url = receipt_data.get("image_url")
        
        # In production: Call Claude Vision or Google Document AI
        extracted = await self._ocr_receipt(image_url)
        
        # Create normalized transaction
        transaction = RawTransaction(
            source="receipt_scan",
            external_id=f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            date=extracted.get("date", datetime.now()),
            amount=-abs(extracted.get("total", 0)),  # Expenses are negative
            description=f"Receipt: {extracted.get('vendor', 'Unknown')}",
            vendor_payee=extracted.get("vendor"),
            raw_data=extracted,
            confidence_score=extracted.get("confidence", 0.8),
            requires_review=extracted.get("confidence", 0.8) < 0.85
        )
        
        return {
            "source": "receipt_scan",
            "transactions": [self._transaction_to_dict(transaction)],
            "extraction_confidence": extracted.get("confidence", 0.8),
            "requires_review": transaction.requires_review
        }
        
    async def _process_invoice(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """
        Process contractor invoice (both payables and receivables).
        
        Contractor-specific handling:
        - Progress billing recognition
        - Retention tracking
        - Job costing allocation
        """
        invoice_data = task.payload.get("invoice", {})
        invoice_type = invoice_data.get("type", "payable")  # payable or receivable
        
        # Extract structured data
        extracted = await self._parse_invoice(invoice_data)
        
        # For receivables: Track as income when billed (accrual) or received (cash)
        # Most contractors use cash basis, so we note it but don't book until paid
        
        transaction = RawTransaction(
            source="invoice_upload",
            external_id=f"inv_{extracted.get('invoice_number', 'unknown')}",
            date=extracted.get("date", datetime.now()),
            amount=extracted.get("total", 0) if invoice_type == "receivable" else -extracted.get("total", 0),
            description=f"Invoice #{extracted.get('invoice_number')}: {extracted.get('customer_vendor')}",
            vendor_payee=extracted.get("customer_vendor"),
            raw_data={
                **extracted,
                "type": invoice_type,
                "job_id": extracted.get("job_id"),
                "retention_amount": extracted.get("retention", 0),
                "line_items": extracted.get("line_items", [])
            },
            confidence_score=0.95,
            requires_review=extracted.get("retention", 0) > 0  # Flag if retention involved
        )
        
        return {
            "source": "invoice",
            "invoice_type": invoice_type,
            "transactions": [self._transaction_to_dict(transaction)],
            "job_costing_data": extracted.get("line_items", [])
        }
        
    async def _process_statement(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """
        Process bank/credit card statement PDF.
        Useful for historical data or accounts without API access.
        """
        statement_url = task.payload.get("statement_url")
        statement_type = task.payload.get("statement_type", "bank")
        
        # In production: PDF extraction service
        extracted_transactions = await self._parse_statement_pdf(statement_url)
        
        processed = []
        for txn in extracted_transactions:
            normalized = RawTransaction(
                source=f"statement_{statement_type}",
                external_id=txn.get("ref_number", f"stmt_{len(processed)}"),
                date=txn.get("date", datetime.now()),
                amount=txn.get("amount", 0),
                description=txn.get("description", ""),
                vendor_payee=self._extract_vendor(txn.get("description", "")),
                raw_data=txn,
                confidence_score=0.85,
                requires_review=False
            )
            
            if not self._is_duplicate(normalized, client.client_id):
                processed.append(normalized)
                
        return {
            "source": f"statement_{statement_type}",
            "transactions_extracted": len(extracted_transactions),
            "transactions_new": len(processed),
            "transactions": [self._transaction_to_dict(t) for t in processed]
        }
        
    async def _process_email_attachment(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """
        Process documents from email attachments.
        Integrates with client's email to auto-capture invoices/receipts.
        """
        email_data = task.payload.get("email", {})
        attachments = email_data.get("attachments", [])
        
        results = []
        for attachment in attachments:
            file_type = attachment.get("content_type", "")
            
            if "pdf" in file_type:
                # Could be invoice or statement
                result = await self._classify_and_process_pdf(attachment, client)
                results.append(result)
            elif "image" in file_type:
                # Likely a receipt
                result = await self._process_receipt(
                    Task(
                        task_id="email_receipt",
                        task_type=AgentType.INGESTION,
                        client_id=client.client_id,
                        payload={"receipt": {"image_url": attachment.get("url")}}
                    ),
                    client
                )
                results.append(result)
                
        return {
            "source": "email_attachment",
            "attachments_processed": len(attachments),
            "results": results
        }
        
    # Helper Methods
    
    async def _normalize_bank_transaction(
        self, 
        raw: Dict[str, Any], 
        client: ClientProfile
    ) -> RawTransaction:
        """Normalize bank transaction to standard format."""
        
        # Extract vendor from description
        description = raw.get("name", raw.get("description", ""))
        vendor = self._extract_vendor(description)
        
        return RawTransaction(
            source="bank_feed",
            external_id=raw.get("transaction_id", raw.get("id", "")),
            date=datetime.fromisoformat(raw.get("date", datetime.now().isoformat())),
            amount=raw.get("amount", 0),
            description=description,
            vendor_payee=vendor,
            raw_data=raw,
            confidence_score=1.0,
            requires_review=False
        )
        
    def _extract_vendor(self, description: str) -> Optional[str]:
        """
        Extract normalized vendor name from transaction description.
        Uses pattern matching and known vendor database.
        """
        description_upper = description.upper()
        
        # Check against known patterns
        for pattern, vendor in self.vendor_patterns.items():
            if re.search(pattern, description_upper):
                return vendor
                
        # Fall back to cleaning the description
        # Remove common banking prefixes
        cleaned = re.sub(
            r'^(POS|ACH|DEBIT|CREDIT|PURCHASE|PAYMENT|TRANSFER)\s+',
            '',
            description,
            flags=re.IGNORECASE
        )
        
        # Take first meaningful segment
        parts = cleaned.split()
        if parts:
            return ' '.join(parts[:3])  # First 3 words
            
        return None
        
    def _load_vendor_patterns(self) -> Dict[str, str]:
        """
        Load vendor recognition patterns.
        In production: This would be ML-based and continuously improved.
        """
        return {
            r'HOME\s*DEPOT': 'The Home Depot',
            r'LOWES': "Lowe's",
            r'GRAINGER': 'W.W. Grainger',
            r'FERGUSON': 'Ferguson Enterprises',
            r'JOHNSTONE': 'Johnstone Supply',
            r'CARRIER': 'Carrier HVAC',
            r'LENNOX': 'Lennox Industries',
            r'TRANE': 'Trane Technologies',
            r'SHERWIN': 'Sherwin-Williams',
            r'FASTENAL': 'Fastenal',
            r'MENARDS': 'Menards',
            r'ACE\s*HARDWARE': 'Ace Hardware',
            r'NORTHERN\s*TOOL': 'Northern Tool',
            r'HARBOR\s*FREIGHT': 'Harbor Freight',
            r'AUTOZONE': 'AutoZone',
            r'O\'?REILLY': "O'Reilly Auto",
            r'SHELL': 'Shell Gas',
            r'EXXON': 'ExxonMobil',
            r'CHEVRON': 'Chevron',
            r'BP': 'BP Gas',
            r'QUIKTRIP|QT\s': 'QuikTrip',
            r'RACETRAC': 'RaceTrac',
            r'WAWA': 'Wawa',
            r'7-?ELEVEN|7-?11': '7-Eleven',
        }
        
    def _is_duplicate(self, transaction: RawTransaction, client_id: str) -> bool:
        """Check if transaction has already been processed."""
        key = f"{client_id}:{transaction.source}:{transaction.external_id}"
        return key in self.known_transactions
        
    def _mark_seen(self, transaction: RawTransaction, client_id: str):
        """Mark transaction as processed."""
        key = f"{client_id}:{transaction.source}:{transaction.external_id}"
        self.known_transactions[key] = datetime.now()
        
    # OCR and Extraction Methods (Stubs for Production Integration)
    
    async def _ocr_receipt(self, image_url: str) -> Dict[str, Any]:
        """
        OCR receipt image.
        Production: Claude Vision API or Google Document AI
        """
        # Simulated extraction
        return {
            "vendor": "The Home Depot",
            "date": datetime.now(),
            "subtotal": 156.78,
            "tax": 12.54,
            "total": 169.32,
            "payment_method": "card",
            "confidence": 0.92,
            "line_items": [
                {"description": "2x4x8 Lumber", "qty": 10, "price": 5.67},
                {"description": "Deck Screws 1lb", "qty": 2, "price": 8.99},
            ]
        }
        
    async def _parse_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse invoice document.
        Production: Structured extraction from PDF/image
        """
        return {
            "invoice_number": invoice_data.get("number", "INV-001"),
            "date": datetime.now(),
            "customer_vendor": invoice_data.get("customer", "Sample Customer"),
            "total": invoice_data.get("amount", 0),
            "retention": invoice_data.get("retention", 0),
            "job_id": invoice_data.get("job_id"),
            "line_items": invoice_data.get("items", [])
        }
        
    async def _parse_statement_pdf(self, statement_url: str) -> List[Dict[str, Any]]:
        """
        Parse bank statement PDF.
        Production: PDF extraction service
        """
        # Simulated extraction
        return [
            {
                "date": datetime.now() - timedelta(days=i),
                "description": f"Transaction {i}",
                "amount": -50.00 * (i + 1),
                "ref_number": f"REF{i:04d}"
            }
            for i in range(5)
        ]
        
    async def _classify_and_process_pdf(
        self, 
        attachment: Dict[str, Any], 
        client: ClientProfile
    ) -> Dict[str, Any]:
        """Classify PDF type and route to appropriate processor."""
        # In production: Use ML to classify document type
        return {"status": "processed", "type": "invoice"}
        
    async def _sync_plaid(
        self, 
        client: ClientProfile, 
        historical: bool = False
    ) -> Dict[str, Any]:
        """Sync transactions from Plaid."""
        # Production: Actual Plaid API integration
        return {
            "source": "plaid",
            "count": 150 if historical else 10,
            "status": "success"
        }
        
    def _transaction_to_dict(self, txn: RawTransaction) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return {
            "source": txn.source,
            "external_id": txn.external_id,
            "date": txn.date.isoformat() if isinstance(txn.date, datetime) else txn.date,
            "amount": txn.amount,
            "description": txn.description,
            "vendor_payee": txn.vendor_payee,
            "confidence_score": txn.confidence_score,
            "requires_review": txn.requires_review
        }
        
    def _result_to_dict(self, result: IngestionResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "source": result.source,
            "transactions_processed": result.transactions_processed,
            "transactions_new": result.transactions_new,
            "transactions_duplicate": result.transactions_duplicate,
            "transactions_flagged": result.transactions_flagged,
            "processing_time_ms": result.processing_time_ms,
            "transactions": [
                self._transaction_to_dict(t) for t in (result.transactions or [])
            ]
        }


# Testing
if __name__ == "__main__":
    async def test_ingestion():
        agent = IngestionAgent()
        
        # Create test client
        client = ClientProfile(
            client_id="test_001",
            business_name="Test HVAC Co",
            trade="HVAC",
            state="GA",
            chart_of_accounts={},
            tax_classification="S-Corp",
            payroll_frequency="bi-weekly"
        )
        
        # Test bank feed processing
        task = Task(
            task_id="test_bank",
            task_type=AgentType.INGESTION,
            client_id="test_001",
            payload={
                "action": "bank_feed",
                "transactions": [
                    {
                        "transaction_id": "txn_001",
                        "date": "2024-01-15",
                        "amount": -169.32,
                        "name": "HOME DEPOT #1234"
                    },
                    {
                        "transaction_id": "txn_002", 
                        "date": "2024-01-15",
                        "amount": -45.00,
                        "name": "SHELL OIL 123456"
                    }
                ]
            }
        )
        
        result = await agent.process(task, client)
        print(json.dumps(result, indent=2, default=str))
        
    asyncio.run(test_ingestion())
