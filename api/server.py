"""
Fynix Systems - API Layer
=========================
FastAPI server for external integrations.

Integrations supported:
- GoHighLevel webhooks
- Plaid bank feed webhooks
- Zapier triggers/actions
- Direct API access
- Slack notifications
- Email delivery
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import json
import hmac
import hashlib
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# In production, import from main
# from main import FynixBookkeepingPlatform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FynixAPI")

app = FastAPI(
    title="Fynix Autonomous Bookkeeping API",
    description="API for the Fynix contractor bookkeeping automation platform",
    version="1.0.0"
)

# CORS for web integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Pydantic Models
# ============================================================================

class ClientOnboardRequest(BaseModel):
    """Request to onboard a new client."""
    business_name: str = Field(..., description="Business name")
    trade: str = Field(..., description="Trade type: HVAC, Plumbing, Roofing, Electrical, General")
    state: str = Field(..., description="State code (e.g., GA)")
    tax_classification: str = Field(default="LLC", description="S-Corp, LLC, Sole Prop")
    payroll_frequency: str = Field(default="bi-weekly", description="weekly, bi-weekly, monthly")
    owner_email: str = Field(..., description="Primary contact email")
    owner_phone: Optional[str] = Field(None, description="Primary contact phone")
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "Cool Comfort HVAC",
                "trade": "HVAC",
                "state": "GA",
                "tax_classification": "S-Corp",
                "payroll_frequency": "bi-weekly",
                "owner_email": "owner@coolcomforthvac.com"
            }
        }


class BankTransaction(BaseModel):
    """A single bank transaction."""
    transaction_id: str
    date: str
    amount: float
    name: str
    category: Optional[str] = None
    pending: bool = False


class BankFeedWebhook(BaseModel):
    """Webhook payload for bank feed updates (Plaid format)."""
    webhook_type: str
    webhook_code: str
    item_id: str
    new_transactions: int = 0
    removed_transactions: List[str] = []
    

class ReportRequest(BaseModel):
    """Request to generate a report."""
    client_id: str
    report_type: str = Field(..., description="flash, monthly, job_profitability, cash_flow, tax_planning, bank_ready")
    period: Optional[str] = Field(None, description="Period for report (e.g., 2024-10)")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ReceiptUpload(BaseModel):
    """Receipt image upload."""
    client_id: str
    image_url: str
    source: str = "upload"  # upload, email, mobile


class InvoiceData(BaseModel):
    """Invoice data for processing."""
    client_id: str
    invoice_type: str = "receivable"  # receivable or payable
    invoice_number: str
    customer_vendor: str
    amount: float
    date: str
    job_id: Optional[str] = None
    line_items: List[Dict[str, Any]] = []


class GHLContactWebhook(BaseModel):
    """GoHighLevel contact webhook."""
    type: str
    locationId: str
    contactId: str
    email: Optional[str] = None
    phone: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    companyName: Optional[str] = None
    customFields: Optional[Dict[str, Any]] = None


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API health check."""
    return {
        "service": "Fynix Autonomous Bookkeeping",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "agents": {
            "ingestion": "active",
            "categorization": "active",
            "reporting": "active",
            "compliance": "active"
        },
        "uptime": "operational",
        "last_check": datetime.now().isoformat()
    }


# Client Management
@app.post("/clients/onboard")
async def onboard_client(request: ClientOnboardRequest, background_tasks: BackgroundTasks):
    """
    Onboard a new contractor client.
    
    Triggers:
    - Client profile creation
    - Integration setup
    - Initial compliance check
    - Welcome email sequence
    """
    try:
        client_id = f"client_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # In production: Call platform.onboard_client()
        
        # Trigger background onboarding tasks
        background_tasks.add_task(
            _run_onboarding_workflow,
            client_id,
            request.dict()
        )
        
        return {
            "status": "success",
            "client_id": client_id,
            "message": "Client onboarding initiated",
            "next_steps": [
                "Connect bank accounts via Plaid",
                "Upload historical statements",
                "Review initial compliance calendar"
            ]
        }
        
    except Exception as e:
        logger.error(f"Onboarding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/clients/{client_id}/status")
async def get_client_status(client_id: str):
    """Get current status for a client."""
    # In production: Query actual platform
    return {
        "client_id": client_id,
        "status": "active",
        "last_sync": datetime.now().isoformat(),
        "pending_items": 3,
        "compliance_status": "good"
    }


# Bank Feed Integration
@app.post("/webhooks/plaid")
async def plaid_webhook(payload: BankFeedWebhook, background_tasks: BackgroundTasks):
    """
    Handle Plaid bank feed webhooks.
    
    Webhook types:
    - TRANSACTIONS: New transactions available
    - ITEM: Account connection status changes
    """
    logger.info(f"Plaid webhook: {payload.webhook_type}/{payload.webhook_code}")
    
    if payload.webhook_type == "TRANSACTIONS":
        if payload.webhook_code in ["INITIAL_UPDATE", "HISTORICAL_UPDATE", "DEFAULT_UPDATE"]:
            # Queue transaction sync
            background_tasks.add_task(
                _sync_plaid_transactions,
                payload.item_id,
                payload.new_transactions
            )
            
    return {"status": "received"}


@app.post("/transactions/process")
async def process_transactions(
    client_id: str,
    transactions: List[BankTransaction],
    background_tasks: BackgroundTasks
):
    """
    Process bank transactions for categorization.
    
    Can be called directly or triggered by webhook.
    """
    task_id = f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    background_tasks.add_task(
        _process_transaction_batch,
        client_id,
        [t.dict() for t in transactions],
        task_id
    )
    
    return {
        "status": "processing",
        "task_id": task_id,
        "transaction_count": len(transactions)
    }


# Receipt/Invoice Processing
@app.post("/receipts/upload")
async def upload_receipt(receipt: ReceiptUpload, background_tasks: BackgroundTasks):
    """
    Process uploaded receipt image (URL-based).

    Triggers OCR extraction and categorization.
    """
    task_id = f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    background_tasks.add_task(
        _process_receipt,
        receipt.client_id,
        receipt.image_url,
        task_id
    )

    return {
        "status": "processing",
        "task_id": task_id,
        "message": "Receipt submitted for processing"
    }


@app.post("/api/receipts/capture")
async def capture_receipt(
    file: UploadFile,
    job_id: Optional[str] = None,
    client_id: str = "default_client"
):
    """
    Capture and process a receipt file using Claude Vision OCR.

    Args:
        file: Receipt image file (JPG, PNG, PDF)
        job_id: Optional manual job assignment
        client_id: Client identifier

    Returns:
        Extracted receipt data and job match suggestions
    """
    # Check if this is a demo session
    is_demo = client_id.startswith("demo_")
    if is_demo:
        logger.info(f"Demo mode receipt capture for: {client_id}")

    try:
        # Import OCR module
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from agents.receipt_ocr import ReceiptOCR
        from agents.job_matcher import JobMatcher, Job, ReceiptData

        # Read file
        contents = await file.read()

        # Determine media type
        media_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }

        file_ext = file.filename.split('.')[-1].lower()
        media_type = media_type_map.get(file_ext, 'image/jpeg')

        # Extract data using Claude Vision
        ocr = ReceiptOCR()
        extracted = await ocr.extract_from_bytes(contents, media_type)

        # Generate unique receipt ID
        receipt_id = f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        # Mock active jobs (in production, fetch from database)
        active_jobs = [
            Job(
                job_id="job_001",
                job_number="JOB2024-001",
                customer_name="Smith Residence",
                address="123 Main St",
                trade_type="HVAC",
                start_date=datetime(2025, 12, 26),
                end_date=datetime(2025, 12, 28),
                status="active",
                scope_keywords=["refrigerant", "AC unit", "3-ton", "condenser"],
                estimated_material_cost=500.00
            ),
            Job(
                job_id="job_002",
                job_number="JOB2024-002",
                customer_name="Johnson Property",
                address="456 Oak Ave",
                trade_type="Plumbing",
                start_date=datetime(2025, 12, 25),
                end_date=datetime(2025, 12, 30),
                status="active",
                scope_keywords=["water heater", "pipes", "fixtures"],
                estimated_material_cost=800.00
            ),
            Job(
                job_id="job_003",
                job_number="JOB2024-003",
                customer_name="Wilson HVAC Maintenance",
                address="789 Pine Rd",
                trade_type="HVAC",
                start_date=datetime(2025, 12, 20),
                end_date=None,
                status="active",
                scope_keywords=["maintenance", "filter", "refrigerant"],
                estimated_material_cost=300.00
            )
        ]

        # Match to jobs
        matcher = JobMatcher()
        receipt_data = ReceiptData(
            vendor=extracted.vendor,
            date=extracted.date,
            total=extracted.total,
            tax=extracted.tax or 0.0,
            line_items=extracted.line_items
        )

        job_matches = await matcher.match_receipt_to_job(
            receipt=receipt_data,
            active_jobs=active_jobs,
            manual_job_code=job_id
        )

        result = {
            "receipt_id": receipt_id,
            "extracted": {
                "vendor": extracted.vendor,
                "date": extracted.date.strftime('%Y-%m-%d'),
                "total": extracted.total,
                "tax": extracted.tax,
                "confidence": extracted.confidence,
                "line_items": extracted.line_items,
                "payment_method": extracted.payment_method,
                "receipt_number": extracted.receipt_number
            },
            "job_suggestions": [
                {
                    "job_id": match.job_id,
                    "job_number": match.job_number,
                    "job_name": match.job_name,
                    "confidence": match.confidence,
                    "reasons": match.reasons
                }
                for match in job_matches
            ],
            "status": "extracted" if extracted.confidence > 0.5 else "needs_review",
            "demo_mode": is_demo
        }

        # For demo mode, don't persist to database
        # In production, you would save non-demo receipts to database here

        return result

    except ImportError as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"OCR module not available. Install dependencies: pip install anthropic. Error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Receipt processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/invoices/process")
async def process_invoice(invoice: InvoiceData, background_tasks: BackgroundTasks):
    """
    Process an invoice (AR or AP).
    """
    task_id = f"inv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    background_tasks.add_task(
        _process_invoice,
        invoice.dict(),
        task_id
    )
    
    return {
        "status": "processing",
        "task_id": task_id,
        "invoice_number": invoice.invoice_number
    }


# Reporting
@app.post("/reports/generate")
async def generate_report(request: ReportRequest):
    """
    Generate a report for a client.
    
    Report types:
    - flash: Weekly executive summary
    - monthly: Full monthly package
    - job_profitability: Job costing analysis
    - cash_flow: 12-week cash flow forecast
    - tax_planning: Tax planning summary
    - bank_ready: Bank/loan ready package
    """
    # In production: Call platform.generate_report()
    
    # For demo, return sample structure
    report_samples = {
        "flash": {
            "report_type": "flash",
            "client_id": request.client_id,
            "generated_at": datetime.now().isoformat(),
            "vital_signs": {
                "cash_position": {"current": 34500.00, "status": "healthy"},
                "revenue_this_week": {"amount": 12500.00, "vs_last_week": "+15%"},
                "gross_margin": {"current": "47%", "status": "on_track"}
            }
        },
        "cash_flow": {
            "report_type": "cash_flow",
            "client_id": request.client_id,
            "summary": {
                "current_cash": 34500.00,
                "projected_low": 8200.00,
                "projected_low_week": "Week 6"
            }
        }
    }
    
    return report_samples.get(request.report_type, {"error": "Unknown report type"})


@app.get("/reports/{client_id}/flash")
async def get_flash_report(client_id: str):
    """Quick access to latest flash report."""
    return await generate_report(ReportRequest(
        client_id=client_id,
        report_type="flash"
    ))


# Compliance
@app.get("/compliance/{client_id}/status")
async def get_compliance_status(client_id: str):
    """Get compliance status for a client."""
    # In production: Call platform.check_compliance()
    return {
        "client_id": client_id,
        "checked_at": datetime.now().isoformat(),
        "summary": {
            "overall_status": "good",
            "critical": 0,
            "high": 1,
            "upcoming": 4
        },
        "alerts": [
            {
                "item": "Commercial Auto Insurance",
                "message": "Renewal due in 28 days",
                "severity": "high"
            }
        ]
    }


@app.get("/compliance/{client_id}/calendar")
async def get_compliance_calendar(client_id: str):
    """Get 12-month compliance calendar."""
    return {
        "client_id": client_id,
        "calendar": {
            "2024-11": [
                {"name": "Auto Insurance Renewal", "due": "November 15"}
            ],
            "2024-12": [
                {"name": "Q4 Estimated Taxes", "due": "December 15"}
            ],
            "2025-01": [
                {"name": "W-2s to Employees", "due": "January 31"},
                {"name": "1099s to Contractors", "due": "January 31"},
                {"name": "Business License Renewal", "due": "January 31"}
            ]
        }
    }


# GoHighLevel Integration
@app.post("/webhooks/ghl/contact")
async def ghl_contact_webhook(
    payload: GHLContactWebhook,
    background_tasks: BackgroundTasks
):
    """
    Handle GoHighLevel contact webhooks.
    
    Used for:
    - New lead onboarding
    - Client status updates
    - Trigger automated workflows
    """
    logger.info(f"GHL webhook: {payload.type} for contact {payload.contactId}")
    
    if payload.type == "ContactCreate":
        # Check if this is a bookkeeping lead
        custom_fields = payload.customFields or {}
        
        if custom_fields.get("service_interest") == "bookkeeping":
            background_tasks.add_task(
                _handle_new_bookkeeping_lead,
                payload.dict()
            )
            
    return {"status": "received"}


# Zapier Integration
@app.post("/zapier/trigger/new-report")
async def zapier_new_report_trigger():
    """
    Zapier trigger: New report available.
    Returns latest reports for polling.
    """
    return {
        "reports": [
            {
                "id": "report_001",
                "client_id": "client_001",
                "type": "flash",
                "generated_at": datetime.now().isoformat()
            }
        ]
    }


@app.post("/zapier/trigger/compliance-alert")
async def zapier_compliance_alert_trigger():
    """
    Zapier trigger: New compliance alert.
    """
    return {
        "alerts": [
            {
                "id": "alert_001",
                "client_id": "client_001",
                "item": "Auto Insurance",
                "message": "Renewal due in 28 days",
                "severity": "high"
            }
        ]
    }


@app.post("/zapier/action/create-client")
async def zapier_create_client(request: ClientOnboardRequest, background_tasks: BackgroundTasks):
    """
    Zapier action: Create new client.
    """
    return await onboard_client(request, background_tasks)


# ============================================================================
# Background Task Functions
# ============================================================================

async def _run_onboarding_workflow(client_id: str, client_data: Dict[str, Any]):
    """Run full onboarding workflow in background."""
    logger.info(f"Running onboarding for {client_id}")
    # In production: Execute full onboarding sequence
    await asyncio.sleep(1)  # Simulate work
    logger.info(f"Onboarding complete for {client_id}")


async def _sync_plaid_transactions(item_id: str, count: int):
    """Sync transactions from Plaid."""
    logger.info(f"Syncing {count} transactions for item {item_id}")
    # In production: Call Plaid API and process
    await asyncio.sleep(1)


async def _process_transaction_batch(
    client_id: str, 
    transactions: List[Dict], 
    task_id: str
):
    """Process a batch of transactions."""
    logger.info(f"Processing {len(transactions)} transactions for {client_id}")
    # In production: Call ingestion and categorization agents
    await asyncio.sleep(1)


async def _process_receipt(client_id: str, image_url: str, task_id: str):
    """Process receipt image."""
    logger.info(f"Processing receipt {task_id} for {client_id}")
    # In production: Call OCR service and categorization
    await asyncio.sleep(1)


async def _process_invoice(invoice_data: Dict, task_id: str):
    """Process invoice."""
    logger.info(f"Processing invoice {task_id}")
    await asyncio.sleep(1)


async def _handle_new_bookkeeping_lead(contact_data: Dict):
    """Handle new bookkeeping lead from GHL."""
    logger.info(f"New bookkeeping lead: {contact_data.get('email')}")
    # In production: Start lead nurture sequence
    await asyncio.sleep(1)


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize platform on startup."""
    logger.info("Starting Fynix API server...")
    # In production: Initialize platform
    

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("Shutting down Fynix API server...")


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
